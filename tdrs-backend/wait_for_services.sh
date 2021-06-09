#!/usr/bin/env bash
wait-for-it \
    --service http://clamav-rest:9000 \
    --service http://localstack:4566/health \
    --timeout 60 \
    -- echo "ClamAV and Localstack are ready!"

# NOTE: Consider deprecating this script and using the above command instead.
python wait_for_postgres.py
