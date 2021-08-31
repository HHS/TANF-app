#!/bin/bash
set -e

if ! [ -x "$(command -v truffleHog)" ]; then
    echo The command truffleHog is not available, installing...

    # Install truffleHog in a venv
    python -m venv trufflehog-check
    source trufflehog-check/bin/activate
    python -m pip install --upgrade pip
    pip install truffleHog
else
    echo The command truffleHog is available
fi

echo "trufflehog-check.sh: Scanning repo ..."

last_merge=$(git log --format=format:"%H" -n 1 raft-tdp-main)

# $1 - The first argument to this script, the current git branch name
# --since_commit - Look at all commits since the last merge into raft-tdp-main
# --entropy=True - Entropy checks on large git diffs
python ./trufflehog-check/lib/python3.8/site-packages/truffleHog/truffleHog.py \
  --regex \
  --entropy=True \
  --branch "$1" \
  --since_commit "$last_merge" \
  --exclude_paths ./trufflehog-exclude-patterns.txt \
  --rules ./regexes.json \
  https://github.com/raft-tech/TANF-app

# if there are issues, they will be listed then script will abort here

echo "trufflehog-check.sh: No issues found"
