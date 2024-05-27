#!/bin/python
#
# Utility scans the GitHub organisation members and check configured yaml file has entries for these members. If yaml
# files contain a user who is not a member, then that user removed from the yaml file

from os import getenv
import base64
import logging
from github import Auth, Github, GithubIntegration, Commit
import yaml
from pathlib import Path

def get_github(gh_token, gh_app_id, gh_app_key_b64):
  if gh_token == None:
    if gh_app_id == None or gh_app_key_b64 == None:
      raise Exception("GitHub Token or GitHub app id and private key must be specified")
    else:
      logging.info("Authenticating with GitHub app")
      gh_app_key = base64.b64decode(gh_app_key_b64).decode("utf-8")
      auth = Auth.AppAuth(gh_app_id, gh_app_key)
      gi = GithubIntegration(auth=auth)
      installation = gi.get_installations()[0]
      return installation.get_github_for_installation()
  else:
    logging.info("Authenticating with GitHub Personal Access Token")
    auth = Auth.Token(gh_token)
    return Github(auth=auth)

def get_member_logins(org):
  logging.info("Collecting organisation members")
  org_member_logins = []
  for member in org.get_members():
    org_member_logins.append(member.login)
  logging.debug(org_member_logins)
  return org_member_logins

def process_file(yml_file, org_member_loging):
  logging.info("Loading content from yaml file")
  is_changed=False
  logging.info("Compare the yml file users to GitHub organisation users")
  with open(yml_file,'r') as file:
    content = yaml.safe_load(file)
    if 'users' in content:
      yml_users = content['users']
      for user_key in yml_users:
        logging.debug("Analysing user {}".format(user_key))
        if 'github_handle' in yml_users[user_key]:
          # Check whether user is a member of GitHub org
          user_github_handle = yml_users[user_key]['github_handle']
          if user_github_handle not in org_member_loging:
            # Check if user state is already set to absent
            if yml_users[user_key]['state'] != 'absent':
              logging.info("Marking user {} as absent as user is not a member of GitHub org".format(user_key))
              yml_users[user_key]['state'] = 'absent'
              is_changed=True
            else:
              logging.debug('User already marked as absent')
        else:
          # Check if user state is already set to absent
          if yml_users[user_key]['state'] != 'absent':          
            logging.info("Marking user {} as absent as github handle is not configured".format(user_key))
            yml_users[user_key]['state'] = 'absent'
            is_changed=True
          else:
            logging.debug('User already marked as absent')
    file.close

  # Fille will be updated if changes are made to users
  is_changed = True
  if is_changed:
    with open(yml_file,'w') as file:
      file.write(yaml.safe_dump(content,sort_keys=False,explicit_start=True))
      file.close

  logging.info("Analysis complete")

def main():
  # Setup logging
  logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  # Extract parameters from environment variables
  gh_token=getenv("GH_TOKEN", None)
  gh_app_id=getenv("GH_APP_ID", None)
  gh_app_key_b64=getenv("GH_APP_KEY_B64", None)
  gh_org=getenv("GH_ORGANISATION", None)
  yml_file=getenv("YML_FILE", None)

  # Check GitHub organisation is configured
  if gh_org == None:
    raise Exception("GitHub organisation must be specified as environment variable")

  if yml_file == None:
    raise Exception("Yml file must be specified as environment variable")

  _yml_file = Path(yml_file)
  if not _yml_file.is_file():
    raise Exception("Yml file cannot be found")

  # Get GitHub object
  gh = get_github(gh_token, gh_app_id, gh_app_key_b64)
  org = gh.get_organization(gh_org)

  # Get organisation
  org = gh.get_organization(gh_org)

  # Get list of organisation member logins
  org_member_loging = get_member_logins(org)

  # Load yml file
  process_file(yml_file, org_member_loging)


if __name__ == '__main__':
    main()