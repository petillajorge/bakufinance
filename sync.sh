#!/usr/bin/env bash
set -e

BRANCH=$(git rev-parse --abbrev-ref HEAD)
REMOTE="origin"

git fetch $REMOTE

if [ "$BRANCH" != "develop" ] && [ "$BRANCH" != "main" ]; then
  git rebase $REMOTE/develop || git rebase --abort
  git push --force-with-lease $REMOTE $BRANCH
else
  git pull --ff-only $REMOTE $BRANCH
  git push $REMOTE $BRANCH
fi
