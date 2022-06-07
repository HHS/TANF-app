#!/usr/bin/env bash

KEYS_JSON=$(cf service-key tanf-keys deployer | grep -A4 "{")
if [ -z "$KEYS_JSON" ]; then
  echo "Unable to get service-keys, you may need to login to Cloud.gov first"
  echo "Run cf login --sso and attempt to retry running this script"
  exit 1
fi

# Requires installation of jq - https://stedolan.github.io/jq/download/
CF_USERNAME_DEV=$(echo "$KEYS_JSON" | jq -r '.username')
CF_PASSWORD_DEV=$(echo "$KEYS_JSON" | jq -r '.password')

CF_SPACE="tanf-dev"

{
  echo "cf_password = \"$CF_PASSWORD_DEV\""
  echo "cf_user = \"$CF_USERNAME_DEV\""
  echo "cf_space_name = \"$CF_SPACE\""
} >> ./dev/variables.tfvars
