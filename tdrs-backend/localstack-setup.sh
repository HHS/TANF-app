#!/bin/bash

# Create the bucket used by the Django app
awslocal s3api create-bucket --bucket $AWS_BUCKET --region $AWS_REGION_NAME
