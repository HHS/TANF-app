#!/bin/sh

# Install jq if not present
if ! command -v jq > /dev/null; then
    apk add --no-cache jq
fi

while true; do
    echo "Refreshing credentials..."
    
    # Get credentials from Vault
    vault read -format=json database/role/django-dynamic-role > /tmp/raw.json
    
    # Extract data and format for Django
    jq '.data + {"ENGINE": "django.db.backends.postgresql", "NAME": "tdrs_test", "HOST": "postgres", "PORT": "5432"}' /tmp/raw.json > /vault/secrets/database-sidecar.json
    
    echo "Credentials refreshed at $(date)"
    sleep 30
done