#!/bin/bash
set -e

if command -v git-secrets /dev/null 2>&1; then
    echo The command git secrets is available
else
    echo The command git secrets is not available, installing...
    oldpwd=$PWD
    cd /tmp/
    git clone git@github.com:awslabs/git-secrets.git
    cd git-secrets
    if command -v make /dev/null 2>&1; then
        echo The command make is available
    else
        echo The command make is not available, installing...
        apt-get update && apt-get install -y make
    fi
    make install
    cd $oldpwd
    #rm -rf /tmp/git-secrets
fi

# ensure we have correct configs in place
[ -f ../.gitconfig ]
cat ../.gitconfig >> .git/config 
git-secrets --scan -r ../