#!/usr/bin/env bash
set -e

sudo apt-get update

# shellcheck source=/dev/null
source /opt/circleci/.nvm/nvm.sh || true

./scripts/install-go.sh
# shellcheck source=/dev/null
. "$BASH_ENV"

sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b "$HOME/go/bin"
go install gotest.tools/gotestsum@latest

task --version
gotestsum --version
