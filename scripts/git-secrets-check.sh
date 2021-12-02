#!/bin/bash
set -e

if [ -d /tmp/git-secrets ]; then
    echo The command git-secrets is available
else
    echo The command git-secrets is not available, cloning...
    git clone git@github.com:awslabs/git-secrets.git /tmp/git-secrets/
    if [ -f /tmp/git-secrets/git-secrets ]; then
        sudo cp /tmp/git-secrets/git-secrets /usr/sbin/
    else
        git clone https://github.com/awslabs/git-secrets.git /tmp/git-secrets
    fi
fi

# ensure we have correct configs in place
[ -f ../.gitconfig ]
cat .gitconfig >> .git/config 
echo "Git-Secrets Config loaded:"
grep -A10 secrets .git/config
# grep will return non-zero code if nothing found, failing the build

#PATH="$PATH:/tmp/git-secrets" What if we just copy into somewhere in the PATH?

echo "git-secrets-check.sh: Scanning repo ..."
#/tmp/git-secrets/
git secrets --scan -r ../

# if there are issues, they will be listed then script will abort here
if [[ $? -eq 0 ]]; then
 echo "git-secrets-check.sh: No issues found"
else
  echo "git-secrets-check.sh: Issues found with return code $?, please remediate."
  return -1
fi

