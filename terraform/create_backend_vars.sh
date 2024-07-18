#!/usr/bin/env bash

if [[ $# -eq 0 ]] ; then
    echo 'You need to pass the env you are configuring: 'dev', 'staging', 'production'.'
    exit 1
fi

if [[ "$1" != "dev" && "$1" != "staging" && "$1" != "production" ]] ; then
  echo 'The first argument to this script must be one of: 'dev', 'staging', or 'production'.'
  exit 1
fi

S3_CREDENTIALS=$(cf service-key tdp-tf-states tdp-tf-key | tail -n +2)
if [ -z "$S3_CREDENTIALS" ]; then
  echo "Unable to get service-keys, you may need to login to Cloud.gov first"
  echo "Run cf login --sso and attempt to retry running this script"
  exit 1
fi

# Requires installation of jq - https://stedolan.github.io/jq/download/
ACCESS_KEY=$(echo "${S3_CREDENTIALS}" | jq -r '.credentials.access_key_id')
SECRET_KEY=$(echo "${S3_CREDENTIALS}" | jq -r '.credentials.secret_access_key')
REGION=$(echo "${S3_CREDENTIALS}" | jq -r '.credentials.region')
BUCKET=$(echo "${S3_CREDENTIALS}" | jq -r '.credentials.bucket')

{
  echo "access_key = \"$ACCESS_KEY\""
  echo "secret_key = \"$SECRET_KEY\""
  echo "region = \"$REGION\""
  echo "bucket = \"$BUCKET\""
} > ./$1/backend_config.tfvars
