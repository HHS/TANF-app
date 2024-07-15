#!/usr/bin/env bash

if [[ $# -eq 0 ]] ; then
    echo 'You need to pass the env you are configuring: 'dev', 'staging', 'production'.'
    exit 1
fi

if [[ "$1" != "dev" && "$1" != "staging" && "$1" != "production" ]] ; then
  echo 'The first argument to this script must be one of: 'dev', 'staging', or 'production'.'
  exit 1
fi

KEYS_JSON=$(cf service-key tanf-keys deployer | grep -A4 "{")
if [ -z "$KEYS_JSON" ]; then
  echo "Unable to get service-keys, you may need to login to Cloud.gov first"
  echo "Run cf login --sso and attempt to retry running this script"
  exit 1
fi

# Requires installation of jq - https://stedolan.github.io/jq/download/
CF_USERNAME_DEV=$(echo "$KEYS_JSON" | jq -r '.credentials.username')
CF_PASSWORD_DEV=$(echo "$KEYS_JSON" | jq -r '.credentials.password')

CF_SPACE="tanf-dev"

{
  echo "cf_password = \"$CF_PASSWORD_DEV\""
  echo "cf_user = \"$CF_USERNAME_DEV\""
  echo "cf_space_name = \"$CF_SPACE\""
} > ./$1/variables.tfvars
