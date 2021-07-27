#!/usr/bin/env bash
set -e
if command -v codecov > /dev/null 2>&1; then
  echo The command codecov is available
else
  echo The command codecov is not available, installing...
  set -x

  echo Importing Codecov PGP public keys...
  curl https://keybase.io/codecovsecurity/pgp_keys.asc | gpg --import

  echo Downloading codecov uploader...
  curl -Os https://uploader.codecov.io/latest/linux/codecov

  echo Downloading SHA signatures...
  curl -Os https://uploader.codecov.io/latest/linux/codecov.SHA256SUM
  curl -Os https://uploader.codecov.io/latest/linux/codecov.SHA256SUM.sig

  echo Verifying package integrity...
  sha256sum -c codecov.SHA256SUM
  gpg --verify codecov.SHA256SUM.sig codecov.SHA256SUM

  echo Validation successful, completing installation...
  chmod +x codecov
  rm codecov.SHA256SUM
  rm codecov.SHA256SUM.sig
  sudo mv codecov /usr/bin/
fi
