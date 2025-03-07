#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else
    mv ../bin/linux/jq /usr/local/bin/jq
    mv ../bin/linux/yq /usr/local/bin/yq
    mv ../bin/linux/cf8 /usr/local/bin/cf
    jq --version
    yq --version
    cf --version
fi
