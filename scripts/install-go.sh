#!/usr/bin/env bash

set -euo pipefail

go_version=$(awk '/^go / { print $2; exit }' tdrs-services/parser/go.mod)
if [[ -z "$go_version" ]]; then
  echo "Failed to determine Go version from tdrs-services/parser/go.mod" >&2
  exit 1
fi

install_dir="$HOME/.local/go-${go_version}"
if [[ ! -x "$install_dir/bin/go" ]]; then
  archive=$(mktemp)
  extract_dir=$(mktemp -d)
  trap 'rm -f "$archive"; rm -rf "$extract_dir"' EXIT

  curl -fsSL "https://go.dev/dl/go${go_version}.linux-amd64.tar.gz" -o "$archive"
  tar -C "$extract_dir" --strip-components=1 -xzf "$archive"
  mkdir -p "$(dirname "$install_dir")"
  mv "$extract_dir" "$install_dir"
fi

export PATH="$install_dir/bin:$HOME/go/bin:$PATH"
if [[ -n "${BASH_ENV:-}" ]]; then
  echo "export PATH=\"$install_dir/bin:\$HOME/go/bin:\$PATH\"" >>"$BASH_ENV"
fi
go version
