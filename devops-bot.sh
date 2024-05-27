#!/bin/bash

git config --global user.name devops-bot
git config --global user.email devops@consensys.net

HASH=$(md5sum file.yml | sed 's/\(^[^ ]*\).*/\1/g' | cut -c 1-10)
BRANCH_NAME=git-bot-$HASH


# Check PR has alredy created. This is to avoid creating multiple PRs for same change
PR_COUNT=$(eval "gh pr list --state all --json title  -q '.[] | select(.title | contains(\"$HASH\"))' | wc -l")

# Create PR if no previous PR containing the hash
if [[ $PR_COUNT -eq 0 ]]
then
  echo "Creating PR"
  git checkout -b git-bot-$HASH
  git add file.yml
  git commit -m "Changes to file $HASH" file.yml
  git push -f origin $BRANCH_NAME

  gh pr create --base main --title "Bot changes $HASH" \
    --body "Changes to file.yml"
else
  echo "WARN: Previous PR found with same hash. Not creating another PR"
fi