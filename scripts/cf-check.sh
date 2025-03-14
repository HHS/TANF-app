#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else
    if [[ -f /bin/terraform ]]; then
        echo "This is our Terraform executor, Alpine Linux v3.13"
        apk update
        apk add curl jq
    else
        apt-get update
        apt-get install curl wget gnupg2 apt-transport-https jq
    fi
    wget https://github.com/cloudfoundry/cli/releases/download/v8.10.0/cf8-cli_8.10.0_linux_x86-64.tgz
    tar -xvf cf8-cli_8.10.0_linux_x86-64.tgz
    mv cf8 /usr/local/bin/cf
    cf --version
fi
