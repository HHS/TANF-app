# Vault Agent PostgreSQL Integration Quick Start

## Setup Commands


# Build base image that includes HVAC dependency
docker build -f Dockerfile.base -t elipe17/tdp-backend-base:latest .

# Update Dockerfile FROM line:
# FROM elipe17/tdp-backend-base:v0.0.2 → FROM elipe17/tdp-backend-base:latest

docker-compose build web
docker-compose up -d vault postgres


## Initialize Vault
docker-compose exec vault sh

# Initialize and record the root token and unseal key
vault operator init -key-shares=1 -key-threshold=1

# Unseal Vault
vault operator unseal your-actual-unseal-key-here

# Set your root token
export VAULT_TOKEN=s.your-actual-root-token-here

# Verify you're authenticated
vault token lookup

Note: if you are on dev environment, then you will need to export the local vault address: "export VAULT_ADDR='http://0.0.0.0:8200'"

## Configure Database Secrets

# Exec into postgres container
docker compose exec postgres sh

# Enable the database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/postgresql \
    plugin_name=postgresql-database-plugin \
    connection_url="postgresql://{{username}}:{{password}}@postgres:5432/tdrs_test?sslmode=disable" \
    allowed_roles="django-dynamic-role" \
    username="tdpuser" \
    password="something_secure"

# Create Database Dynamic Role
vault write database/roles/django-dynamic-role \
    db_name=postgresql \
    creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; \
                        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO \"{{name}}\"; \
                        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO \"{{name}}\"; \
                        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO \"{{name}}\"; \
                        ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO \"{{name}}\";" \
    default_ttl="1h" \
    max_ttl="24h"

# Enable KV Secrets Engine
vault secrets enable -path=kv kv-v2

# Store static database credentials
vault kv put kv/database \
    engine="django.db.backends.postgresql" \
    database="tdrs_test" \
    username="tdpuser" \
    password="something_secure" \
    host="postgres" \
    port="5432"


## Test Credentials


# Test dynamic credentials
vault read database/creds/django-dynamic-role

# Test static credentials
vault kv get kv/database

# Exit the vault container
exit


## Start Services and Test Integration


# Set the token in your environment for docker-compose
export VAULT_TOKEN=<your-root-token>

# Start the vault-agent and web services
docker-compose up -d vault-agent web

# Check if the credentials file was created
docker-compose exec vault-agent cat /vault/secrets/database.json

# Run Django migration to test Vault + Database connection
docker-compose exec web python manage.py migrate

## Rotate Staic KV Keys

# Connect to Vault
docker-compose exec vault sh
export VAULT_TOKEN=your-root-token

# Update the password (or any credential)
vault kv put kv/database \
    engine="django.db.backends.postgresql" \
    database="tdrs_test" \
    username="tdpuser" \
    password="new_secure_password_here" \
    host="postgres" \
    port="5432"

# Verify the update
vault kv get kv/database

# Connect to PostgreSQL and change the user password
docker-compose exec postgres psql -U tdpuser -d tdrs_test
ALTER USER tdpuser WITH PASSWORD 'new_secure_password_here';
\q

# Restart app to pick up new credentials. App only reads credentials at startup
docker-compose restart web