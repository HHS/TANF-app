#!/usr/bin/env bash

KEYS_JSON=$(cf service-key tanf-keys deployer | grep -A4 "{")
if [ -z "$KEYS_JSON" ]; then
  echo "Unable to get service-keys, you may need to login to Cloud.gov first"
  echo "Run cf login --sso and attempt to retry running this script"
  exit 1
fi

# Requires installation of jq - https://stedolan.github.io/jq/download/
CF_USERNAME_STAGING=$(echo "$KEYS_JSON" | jq -r '.username')
CF_PASSWORD_STAGING=$(echo "$KEYS_JSON" | jq -r '.password')
CF_USERNAME_DEV=''
CF_PASSWORD_DEV=''

cd ..
circleci local execute --job deploy-infrastructure-staging \
  -e CF_USERNAME_STAGING="$CF_USERNAME_STAGING" \
  -e CF_PASSWORD_STAGING="$CF_PASSWORD_STAGING" \
  -e CF_USERNAME_DEV="$CF_USERNAME_DEV" \
  -e CF_PASSWORD_DEV="$CF_PASSWORD_DEV" \
  -e CF_ORG=hhs-acf-prototyping \
