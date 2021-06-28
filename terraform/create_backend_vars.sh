#!/usr/bin/env bash

S3_CREDENTIALS=$(cf service-key tdp-tf-states tdp-tf-key | tail -n +2)
if [ -z "$S3_CREDENTIALS" ]; then
  echo "Unable to get service-keys, you may need to login to Cloud.gov first"
  echo "Run cf login --sso and attempt to retry running this script"
  exit 1
fi

# Requires installation of jq - https://stedolan.github.io/jq/download/
ACCESS_KEY=$(echo "${S3_CREDENTIALS}" | jq -r '.access_key_id')
SECRET_KEY=$(echo "${S3_CREDENTIALS}" | jq -r '.secret_access_key')
REGION=$(echo "${S3_CREDENTIALS}" | jq -r '.region')

{
	echo "access_key = \"$ACCESS_KEY\""
	echo "secret_key = \"$SECRET_KEY\""
	echo "region = \"$REGION\""
} >> ./dev/backend_config.tfvars
