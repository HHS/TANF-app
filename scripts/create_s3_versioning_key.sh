#!/bin/bash

# first input is the name of the service
# second input is the name of the service key
SERVICE=$1
KEY_NAME=$2

cf service-key $SERVICE $KEY_NAME > /tmp/cf_aws_creds.json
if sed -n '2p' /tmp/cf_aws_creds.json | grep -q "FAILED"; then
    echo "Service key does not exist"
    cf create-service-key $SERVICE $KEY_NAME
    cf service-key $SERVICE $KEY_NAME > /tmp/cf_aws_creds.json
    echo "key named $KEY_NAME created for service $SERVICE"
else
    circleci-agent step halt
fi
