#!/bin/bash

# Create the bucket used by the Django app
awslocal s3api create-bucket --bucket $AWS_BUCKET --region $AWS_REGION_NAME

# Enable object versioning on the bucket
awslocal s3api put-bucket-versioning --bucket $AWS_BUCKET --versioning-configuration Status=Enabled
