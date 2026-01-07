#!/bin/bash

# Create the bucket used by the Django app
awslocal s3api create-bucket --bucket $AWS_BUCKET --region $AWS_REGION_NAME

# Enable object versioning on the bucket
awslocal s3api put-bucket-versioning --bucket $AWS_BUCKET --versioning-configuration Status=Enabled

# Add bucket for Loki to store logs
awslocal s3api create-bucket --bucket loki-logs --region $AWS_REGION_NAME
awslocal s3api put-bucket-versioning --bucket loki-logs --versioning-configuration Status=Enabled

# Add bucket for Mimir
awslocal s3api create-bucket --bucket mimir-blocks --region $AWS_REGION_NAME
awslocal s3api put-bucket-versioning --bucket mimir-blocks --versioning-configuration Status=Enabled

awslocal s3api create-bucket --bucket mimir-alertmanager --region $AWS_REGION_NAME
awslocal s3api put-bucket-versioning --bucket mimir-alertmanager --versioning-configuration Status=Enabled

awslocal s3api create-bucket --bucket mimir-ruler --region $AWS_REGION_NAME
awslocal s3api put-bucket-versioning --bucket mimir-ruler --versioning-configuration Status=Enabled

awslocal s3api create-bucket --bucket tempo-traces --region $AWS_REGION_NAME
awslocal s3api put-bucket-versioning --bucket tempo-traces --versioning-configuration Status=Enabled
