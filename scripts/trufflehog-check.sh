#!/bin/bash
set -e

pythonVersion="3.10"

if ! [ -x "$(command -v truffleHog)" ]; then
    echo The command truffleHog is not available, installing...

    # Install truffleHog in a venv
    python$pythonVersion -m venv trufflehog-check
    source trufflehog-check/bin/activate
    python -m pip install --upgrade pip
    pip install truffleHog
else
    echo The command truffleHog is available
fi

echo "trufflehog-check.sh: Scanning repo ..."

# $1 - The first argument to this script, the current git branch name
CIRCLE_BRANCH=$1

# Get the hash of the latest commit in the target branch.
last_merge=$(git log --format=format:"%H" -n 1 "$CIRCLE_BRANCH")

# --since_commit - Look at all commits since the last merge into develop
# --entropy=True - Entropy checks on large git diffs
python ./trufflehog-check/lib/python$pythonVersion/site-packages/truffleHog/truffleHog.py \
  --regex \
  --entropy=True \
  --branch "$CIRCLE_BRANCH" \
  --since_commit "$last_merge" \
  --exclude_paths ./trufflehog-exclude-patterns.txt \
  --rules ./regexes.json \
  file:///root/project

# if there are issues, they will be listed then script will abort here

echo "trufflehog-check.sh: No issues found"
