#!/usr/bin/env bash

CGAPPNAME_BACKEND=$1
CG_SPACE=$2

# Determine the appropriate BASE_URL for the deployed instance based on the
# provided Cloud.gov App Name
DEFAULT_ROUTE="https://$CGAPPNAME_BACKEND.app.cloud.gov"
if [ -n "$BASE_URL" ]; then
  # Use Shell Parameter Expansion to replace localhost in the URL
  BASE_URL="${BASE_URL//http:\/\/localhost:8080/$DEFAULT_ROUTE}"
else
  BASE_URL="$DEFAULT_ROUTE/v1"
fi

DEFAULT_FRONTEND_ROUTE="${DEFAULT_ROUTE//backend/frontend}"
if [ -n "$FRONTEND_BASE_URL" ]; then
  FRONTEND_BASE_URL="${FRONTEND_BASE_URL//http:\/\/localhost:3000/$DEFAULT_FRONTEND_ROUTE}"
else
  FRONTEND_BASE_URL="$DEFAULT_FRONTEND_ROUTE"
fi

# Dynamically generate a new DJANGO_SECRET_KEY
DJANGO_SECRET_KEY=$(python -c "from secrets import token_urlsafe; print(token_urlsafe(50))")

# Dynamically set DJANGO_CONFIGURATION based on Cloud.gov Space
DJANGO_SETTINGS_MODULE="tdpservice.settings.cloudgov"
if [ "$CG_SPACE" = "tanf-prod" ]; then
  DJANGO_CONFIGURATION="Production"
elif [ "$CG_SPACE" = "tanf-staging" ]; then
  DJANGO_CONFIGURATION="Staging"
else
  DJANGO_CONFIGURATION="Development"
fi

echo "Setting environment variables for $CGAPPNAME_BACKEND"

cf set-env "$CGAPPNAME_BACKEND" BASE_URL "$BASE_URL"
cf set-env "$CGAPPNAME_BACKEND" DJANGO_SECRET_KEY "$DJANGO_SECRET_KEY"
cf set-env "$CGAPPNAME_BACKEND" FRONTEND_BASE_URL "$FRONTEND_BASE_URL"
cf set-env "$CGAPPNAME_BACKEND" DJANGO_CONFIGURATION "$DJANGO_CONFIGURATION"
cf set-env "$CGAPPNAME_BACKEND" DJANGO_SETTINGS_MODULE "$DJANGO_SETTINGS_MODULE"
