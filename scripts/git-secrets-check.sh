#!/bin/bash
set -e

if [ -d /tmp/git-secrets ]; then
    echo The command git-secrets is available
else
    echo The command git-secrets is not available, cloning...
    git clone git@github.com:awslabs/git-secrets.git /tmp/git-secrets/
fi

# ensure we have correct configs in place
[ -f ../.gitconfig ]
cat ../.gitconfig >> .git/config 
/tmp/git-secrets/git-secrets --scan -r ../