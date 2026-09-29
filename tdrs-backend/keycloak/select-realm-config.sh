#!/bin/bash
set -euo pipefail

REALM_CONFIGS_DIR="${REALM_CONFIGS_DIR:-/opt/keycloak/realm-configs}"
OUTPUT_REALM_PATH="${OUTPUT_REALM_PATH:-/opt/keycloak/data/import/realm-export.json}"
OUTPUT_REALM_DIR="${OUTPUT_REALM_DIR:-$(dirname "$OUTPUT_REALM_PATH")}"
OUTPUT_ADMIN_REALM_PATH="${OUTPUT_ADMIN_REALM_PATH:-${OUTPUT_REALM_DIR}/admin-realm-export.json}"
DEPLOY_ENV="${DEPLOY_ENV:-local}"

case "$DEPLOY_ENV" in
    local|dev)
        SOURCE_REALM_PATH="${REALM_CONFIGS_DIR}/realm-export.dev-local.json"
        SOURCE_ADMIN_REALM_PATH="${REALM_CONFIGS_DIR}/admin-realm-export.dev-local.json"
        ;;
    staging)
        SOURCE_REALM_PATH="${REALM_CONFIGS_DIR}/realm-export.staging.json"
        SOURCE_ADMIN_REALM_PATH="${REALM_CONFIGS_DIR}/admin-realm-export.staging.json"
        ;;
    prod)
        SOURCE_REALM_PATH="${REALM_CONFIGS_DIR}/realm-export.prod.json"
        SOURCE_ADMIN_REALM_PATH="${REALM_CONFIGS_DIR}/admin-realm-export.prod.json"
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

if [ ! -f "$SOURCE_ADMIN_REALM_PATH" ]; then
    echo "ERROR: admin realm config not found at ${SOURCE_ADMIN_REALM_PATH}" >&2
    exit 1
fi

mkdir -p "$OUTPUT_REALM_DIR"
cp "$SOURCE_REALM_PATH" "$OUTPUT_REALM_PATH"
cp "$SOURCE_ADMIN_REALM_PATH" "$OUTPUT_ADMIN_REALM_PATH"

echo "Selected realm configs for DEPLOY_ENV=${DEPLOY_ENV}:"
echo "  standard: ${SOURCE_REALM_PATH} -> ${OUTPUT_REALM_PATH}"
echo "  admin:    ${SOURCE_ADMIN_REALM_PATH} -> ${OUTPUT_ADMIN_REALM_PATH}"
