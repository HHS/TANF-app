#!/bin/bash
set -euo pipefail

REALM_CONFIGS_DIR="${REALM_CONFIGS_DIR:-/opt/keycloak/realm-configs}"
OUTPUT_REALM_PATH="${OUTPUT_REALM_PATH:-/opt/keycloak/data/import/realm-export.json}"
DEPLOY_ENV="${DEPLOY_ENV:-local}"

case "$DEPLOY_ENV" in
    local|dev)
        SOURCE_REALM_PATH="${REALM_CONFIGS_DIR}/realm-export.dev-local.json"
        ;;
    staging)
        SOURCE_REALM_PATH="${REALM_CONFIGS_DIR}/realm-export.staging.json"
        ;;
    prod)
        SOURCE_REALM_PATH="${REALM_CONFIGS_DIR}/realm-export.prod.json"
        ;;
    *)
        echo "ERROR: unsupported DEPLOY_ENV='${DEPLOY_ENV}'" >&2
        exit 1
        ;;
esac

if [ ! -f "$SOURCE_REALM_PATH" ]; then
    echo "ERROR: realm config not found at ${SOURCE_REALM_PATH}" >&2
    exit 1
fi

mkdir -p "$(dirname "$OUTPUT_REALM_PATH")"
cp "$SOURCE_REALM_PATH" "$OUTPUT_REALM_PATH"

echo "Selected realm config for DEPLOY_ENV=${DEPLOY_ENV} from ${SOURCE_REALM_PATH}"
