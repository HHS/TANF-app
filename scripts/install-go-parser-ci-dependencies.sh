#!/usr/bin/env bash
set -e

sudo apt-get update

source /opt/circleci/.nvm/nvm.sh || true

GO_VERSION=$(awk '/^go / { print $2; exit }' tdrs-services/parser/go.mod)
if [ -z "$GO_VERSION" ]; then
  echo "Failed to determine Go version from tdrs-services/parser/go.mod"
  exit 1
fi

curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -o /tmp/go.tar.gz
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf /tmp/go.tar.gz

echo 'export PATH="/usr/local/go/bin:$HOME/go/bin:$PATH"' >> "$BASH_ENV"
. "$BASH_ENV"

go version

sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b "$HOME/go/bin"
go install gotest.tools/gotestsum@latest
go install github.com/sqlc-dev/sqlc/cmd/sqlc@v1.30.0

task --version
gotestsum --version
sqlc version
