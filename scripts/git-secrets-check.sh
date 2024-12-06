#!/bin/bash
set -e
islocal=$1

if [[ $(uname -s) == "Darwin" ]]; then  # Mac OSX check
    gs_path="/usr/local/bin"
else # Linux, we're likely running in CircleCI
    gs_path="/usr/sbin"
fi

if [ -f "$gs_path/git-secrets" ]; then
    echo The command git-secrets is available
else
    echo The command git-secrets is not available, cloning...
    git clone git@github.com:awslabs/git-secrets.git /tmp/git-secrets/
    if [ -f /tmp/git-secrets/git-secrets ]; then

        echo "Moving git secrets into PATH"
        sudo cp /tmp/git-secrets/git-secrets $gs_path/
        $gs_path/git-secrets --install -f
        rm -rf /tmp/git-secrets #cleanup of clone dir
    else
	    echo "Git clone failed for git-secrets"
    fi
fi

# ensure we have correct configs in place
if [ -f .gitconfig ]; then
    cat .gitconfig >> .git/config 
    echo "Git-Secrets Config loaded:"
    grep -A10 secrets .git/config
    # grep will return non-zero code if nothing found, failing the build
fi

if [ $islocal ]; then
    echo "git-secrets-check.sh: Scanning files staged for commit ..."
    setopt shwordsplit
    staged_files=$(git diff --cached --name-status | grep -vE "D|^R[0-9]+"| cut -f2 | xargs)

    for filename in $staged_files; do
        echo "git-secrets-check.sh: Scanning $filename ..."
        git secrets --scan $filename
        retVal=$?
        if [[ $retVal -ne 0 ]]; then
            echo "git-secrets found issues, prevented commit."
            return 1
        fi
    done
    
else
    echo "git-secrets-check.sh: Scanning repo ..."
    git secrets --scan -r ../
    retVal=$?
fi

# if there are issues, they will be listed then script will abort here
if [[ $retVal -eq 0 ]]; then
 echo "git-secrets-check.sh: No issues found"
else
  echo "git-secrets-check.sh: Issues found with return code $retVal, please remediate."
  return 1
fi

#cleanup for testing
rm -rf /tmp/git-secrets
sudo rm -f $gs_path/git-secrets