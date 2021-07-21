#!/usr/bin/env bash
wait-for-it \
    --service http://clamav-rest:9000 \
    --service http://localstack:4566/health \
    --timeout 60 \
    -- echo "ClamAV and Localstack are ready!"

# Wait for Localstack to create the necessary S3 bucket, if in use
if [ "$USE_LOCALSTACK" -eq 1 ]; then
    echo "Waiting 60 seconds for S3 bucket creation"
    # shellcheck disable=SC2091
    until $(
        awslocal s3api head-bucket --bucket "tdp-datafiles-localstack" \
        > /dev/null 2>&1
    ); do
        ((c++)) && ((c==10)) && echo "S3 bucket not found" && exit 1;
        sleep 6;
    done
    echo "S3 Bucket is ready after $((c*6)) seconds"
fi

# NOTE: Consider deprecating this script and using the above command instead.
python wait_for_postgres.py
