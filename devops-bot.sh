#!/bin/bash

git config --global user.name devops-bot
git config --global user.email devops@consensys.net

HASH=$(md5sum file.yml | sed 's/\(^[^ ]*\).*/\1/g' | cut -c 1-10)
BRANCH_NAME=git-bot-$HASH

git checkout -b git-bot-$HASH
git add file.yml
git commit -m "Changes to file $HASH\n devops bot made changes to file" file.yml
git push origin $BRANCH_NAME