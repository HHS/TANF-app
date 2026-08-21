#!/usr/bin/env bash

set -euo pipefail

BACKEND_APP_NAME=${1}
ENVIRONMENT_NAME=${BACKEND_APP_NAME#tdp-backend-}
CELERY_APP_NAME="tdp-celery-$ENVIRONMENT_NAME"
DJANGO_SECRET_KEY=$(python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))")

for app_name in "$BACKEND_APP_NAME" "$CELERY_APP_NAME"; do
  APP_GUID=$(cf app "$app_name" --guid || true)
  if [[ "$APP_GUID" != "FAILED" ]]; then
    cf set-env "$app_name" DJANGO_SECRET_KEY "$DJANGO_SECRET_KEY"
  fi
done
