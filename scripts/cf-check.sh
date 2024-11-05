#!/bin/sh
set -e
if command -v cf /dev/null 2>&1; then
    echo The command cf is available
else
    apt-get update
    apt-get install wget gnupg2 apt-transport-https

    NEXUS_ARCHIVE="cf7-cli_7.7.13_linux_x86-64.tgz"
    NEXUS_URL="https://tdp-nexus.dev.raftlabs.tech/repository/tdp-bin/cloudfoundry-cli/$NEXUS_ARCHIVE"
    curl $NEXUS_URL -o $NEXUS_ARCHIVE  # prefers anonymous, use of -u failed.
    tar xzf $NEXUS_ARCHIVE
    mv ./cf /usr/local/bin/
    chmod +x /usr/local/bin/cf
    cf --version

fi
