#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else
    if [[ -f /bin/terraform ]]; then
        echo "This is our Terraform executor, Alpine Linux v3.13"
        apk update
        apk install curl jq
        if [ $? -ne 0 ]; then
            echo "Failed to install curl and jq"
            apk add --no-cache curl jq
        fi
    else
        apt-get update
        apt-get install curl wget gnupg2 apt-transport-https jq
    fi
    NEXUS_ARCHIVE="cf7-cli_7.7.13_linux_x86-64.tgz"
    NEXUS_URL="https://tdp-nexus.dev.raftlabs.tech/repository/tdp-bin/cloudfoundry-cli/$NEXUS_ARCHIVE"
    curl $NEXUS_URL -o $NEXUS_ARCHIVE  # prefers anonymous, use of -u failed.
    tar xzf $NEXUS_ARCHIVE
    mv ./cf7 /usr/local/bin/cf
    cf --version
fi
