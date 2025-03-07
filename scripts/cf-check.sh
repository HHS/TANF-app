#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else
    mv ../bin/jq /usr/local/bin/jq
    mv ../bin/yq /usr/local/bin/yq
    mv ../bin/cf8 /usr/local/bin/cf
    jq --version
    yq --version
    cf --version
fi
