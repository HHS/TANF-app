#!/usr/bin/env bash
set -euo pipefail
if command -v codecov > /dev/null 2>&1; then
  echo The command codecov is available
else
  echo The command codecov is not available, installing...
  set -x

  echo Importing Codecov PGP public keys...
  curl -fsSL https://uploader.codecov.io/verification.gpg | gpg --import

  echo Downloading codecov uploader...
  curl -Os https://uploader.codecov.io/latest/linux/codecov

  echo Downloading SHA signatures...
  curl -Os https://uploader.codecov.io/latest/linux/codecov.SHA256SUM
  curl -Os https://uploader.codecov.io/latest/linux/codecov.SHA256SUM.sig

  echo Verifying package integrity...
  if command -v sha256sum > /dev/null 2>&1; then
    sha256sum -c codecov.SHA256SUM
  else
    shasum -a 256 -c codecov.SHA256SUM
  fi
  gpg --verify codecov.SHA256SUM.sig codecov.SHA256SUM

  echo Validation successful, completing installation...
  chmod +x ./codecov
  install_dir="/usr/local/bin"
  install_with_sudo=false

  if [ ! -w "$install_dir" ]; then
    if command -v sudo > /dev/null 2>&1; then
      install_with_sudo=true
    else
      install_dir="$HOME/.local/bin"
      mkdir -p "$install_dir"
      export PATH="$install_dir:$PATH"
      if [ -n "${BASH_ENV:-}" ]; then
        echo "export PATH=\"$install_dir:\$PATH\"" >> "$BASH_ENV"
      fi
    fi
  fi

  if [ "$install_with_sudo" = true ]; then
    sudo install -m 0755 ./codecov "$install_dir/codecov"
  else
    install -m 0755 ./codecov "$install_dir/codecov"
  fi

  rm codecov.SHA256SUM
  rm codecov.SHA256SUM.sig
  rm codecov
fi
