#!/usr/bin/env bash

set -euo pipefail

FRONTEND_HOSTNAME=${1}
BACKEND_APP_NAME=${2}
CF_SPACE=${3}

FRONTEND_APP_NAME="tdp-frontend-$FRONTEND_HOSTNAME"
ENVIRONMENT_NAME=${BACKEND_APP_NAME#tdp-backend-}
CELERY_APP_NAME="tdp-celery-$ENVIRONMENT_NAME"

cf map-route "$BACKEND_APP_NAME" apps.internal --hostname "$BACKEND_APP_NAME"
cf map-route "$CELERY_APP_NAME" apps.internal --hostname "$CELERY_APP_NAME"
cf add-network-policy "$FRONTEND_APP_NAME" "$BACKEND_APP_NAME" --protocol tcp --port 8080

if [[ "$CF_SPACE" == "tanf-prod" ]]; then
  cf add-network-policy "$BACKEND_APP_NAME" clamav-rest --protocol tcp --port 9000
else
  SPACE_NAME=${CF_SPACE#tanf-}
  cf add-network-policy "$BACKEND_APP_NAME" "tdp-clamav-nginx-$SPACE_NAME" --protocol tcp --port 9000
fi

if [[ "$CF_SPACE" == "tanf-prod" ]]; then
  cf map-route "$FRONTEND_APP_NAME" tanfdata.acf.hhs.gov
else
  cf map-route "$FRONTEND_APP_NAME" "${FRONTEND_HOSTNAME}.tanfdata.acf.hhs.gov"
fi
