#!/bin/bash
# configure-idps.sh
#
# Post-startup script to configure Keycloak identity providers with
# sensitive material that cannot be expressed in realm-export.json:
#   - Login.gov RSA private key for private_key_jwt client authentication
#   - Login.gov acr_values authorization parameter
#
# Run this AFTER Keycloak has started and imported the realm.
# Prerequisites: curl, jq
#
# Environment variables:
#   KEYCLOAK_URL            - Keycloak base URL (default: http://localhost:8443)
#   KEYCLOAK_ADMIN          - Admin username (default: admin)
#   KEYCLOAK_ADMIN_PASSWORD - Admin password (default: admin)
#   LOGIN_GOV_JWT_KEY       - PEM or base64-encoded Login.gov private key
#   LOGIN_GOV_ACR_VALUES    - ACR values for Login.gov (default: IAL1)
#   SKIP_KEYCLOAK_WAIT      - Set to "true" to skip the health check wait
#                             (useful when running as a CF task after deploy)

set -euo pipefail

KEYCLOAK_MANAGEMENT_URL="${KEYCLOAK_MANAGEMENT_URL:-http://localhost:9001}"
KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8443}"
KEYCLOAK_ADMIN="${KEYCLOAK_ADMIN:-admin}"
KEYCLOAK_ADMIN_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
REALM="tdp"
LOGIN_GOV_ACR_VALUES="${LOGIN_GOV_ACR_VALUES:-http://idmanagement.gov/ns/assurance/ial/1}"

# Wrapper around curl that shows the actual HTTP error response on failure
# instead of silently dying with exit code 22 (curl -f behavior).
# Usage: kc_api [curl_args...] — returns the response body on stdout.
kc_api() {
    local http_code
    http_code=$(curl -s -o /tmp/kc_response.json -w "%{http_code}" "$@")
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        cat /tmp/kc_response.json
    else
        echo "ERROR: API call failed with HTTP ${http_code}" >&2
        echo "  Request: curl $*" >&2
        echo "  Response: $(cat /tmp/kc_response.json 2>/dev/null)" >&2
        return 1
    fi
}

wait_for_keycloak() {
    echo "Waiting for Keycloak at ${KEYCLOAK_MANAGEMENT_URL}..."
    local max_attempts=60
    local attempt=0
    until curl -sf "${KEYCLOAK_MANAGEMENT_URL}/health/ready" > /dev/null 2>&1; do
        attempt=$((attempt + 1))
        echo "  Attempt ${attempt}/${max_attempts} - Keycloak not ready yet..."
        if [ "$attempt" -ge "$max_attempts" ]; then
            echo "ERROR: Keycloak did not become ready after ${max_attempts} attempts"
            exit 1
        fi
        sleep 2
    done
    echo "Keycloak is ready."
}

get_admin_token() {
    local response
    response=$(curl -sf -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${KEYCLOAK_ADMIN}" \
        -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
        -d "grant_type=password" \
        -d "client_id=admin-cli")

    TOKEN=$(echo "$response" | jq -r '.access_token')

    if [ -z "$TOKEN" ] || [ "$TOKEN" == "null" ]; then
        echo "ERROR: Failed to obtain admin access token"
        echo "Response: $response"
        exit 1
    fi
    echo "Admin token obtained."
}

configure_login_gov_signing_key() {
    if [ -z "${LOGIN_GOV_JWT_KEY:-}" ]; then
        echo "WARNING: LOGIN_GOV_JWT_KEY not set, skipping Login.gov signing key configuration."
        echo "  The Login.gov IdP private_key_jwt authentication will not work without it."
        return
    fi

    echo "Configuring Login.gov signing key..."

    # Normalize the private key to PEM format.
    # The env var may be base64-encoded (as in Cloud.gov) or raw PEM.
    local private_key="${LOGIN_GOV_JWT_KEY}"
    if [[ ! "${private_key}" =~ "BEGIN" ]]; then
        private_key=$(echo "${private_key}" | base64 -d 2>/dev/null || echo "${private_key}")
    fi

    # Get the realm's internal ID (needed as parentId for the component)
    local realm_id
    realm_id=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}" \
        -H "Authorization: Bearer ${TOKEN}" | jq -r '.id')

    # Build the RSA key provider component JSON.
    # Priority 200 makes this the active RS256 key, used for:
    #   - Login.gov IdP private_key_jwt client assertion signing
    #   - Keycloak token signing (Django/Grafana verify via JWKS endpoint)
    local key_json
    key_json=$(jq -n \
        --arg realm_id "$realm_id" \
        --arg private_key "$private_key" \
        '{
            name: "login-gov-signing-key",
            parentId: $realm_id,
            providerId: "rsa",
            providerType: "org.keycloak.keys.KeyProvider",
            config: {
                active: ["true"],
                enabled: ["true"],
                priority: ["200"],
                algorithm: ["RS256"],
                privateKey: [$private_key]
            }
        }')

    # Check if the component already exists (idempotent)
    local existing
    existing=$(kc_api \
        "${KEYCLOAK_URL}/admin/realms/${REALM}/components?name=login-gov-signing-key&type=org.keycloak.keys.KeyProvider" \
        -H "Authorization: Bearer ${TOKEN}")

    local count
    count=$(echo "$existing" | jq 'length' 2>/dev/null || echo "0")

    if [ "${count:-0}" -gt "0" ]; then
        local component_id
        component_id=$(echo "$existing" | jq -r '.[0].id')
        key_json=$(echo "$key_json" | jq --arg id "$component_id" '.id = $id')

        kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/components/${component_id}" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$key_json" > /dev/null
        echo "Login.gov signing key updated (component: ${component_id})."
    else
        kc_api -X POST "${KEYCLOAK_URL}/admin/realms/${REALM}/components" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$key_json" > /dev/null
        echo "Login.gov signing key created."
    fi
}

configure_login_gov_acr_values() {
    echo "Configuring Login.gov acr_values..."

    local idp_config
    local http_code
    http_code=$(curl -s -o /tmp/idp_response.json -w "%{http_code}" \
        "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}")
    idp_config=$(cat /tmp/idp_response.json 2>/dev/null || echo '{"alias":null}')

    if [ "$http_code" != "200" ]; then
        echo "WARNING: Login.gov IdP request returned HTTP ${http_code}"
        echo "  Response: $(cat /tmp/idp_response.json 2>/dev/null || echo 'empty')"
        echo "  Skipping acr_values configuration."
        return
    fi

    if [ "$(echo "$idp_config" | jq -r '.alias')" == "null" ]; then
        echo "WARNING: Login.gov IdP not found in realm, skipping acr_values configuration."
        return
    fi

    local auth_url
    auth_url=$(echo "$idp_config" | jq -r '.config.authorizationUrl')

    # Only modify if acr_values not already present
    if [[ "${auth_url}" =~ "acr_values" ]]; then
        echo "acr_values already present in Login.gov authorization URL."
        return
    fi

    # URL-encode the acr_values
    local encoded_acr
    encoded_acr=$(printf '%s' "${LOGIN_GOV_ACR_VALUES}" | sed 's|:|%3A|g; s|/|%2F|g')

    local separator="?"
    if [[ "${auth_url}" =~ "?" ]]; then
        separator="&"
    fi

    local new_url="${auth_url}${separator}acr_values=${encoded_acr}"
    idp_config=$(echo "$idp_config" | jq --arg url "$new_url" '.config.authorizationUrl = $url')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$idp_config" > /dev/null

    echo "Login.gov authorization URL updated with acr_values."
}

configure_master_realm_security_headers() {
    echo "Configuring master realm security headers..."

    local master_realm
    master_realm=$(kc_api "${KEYCLOAK_URL}/admin/realms/master" \
        -H "Authorization: Bearer ${TOKEN}")

    if [ -z "$master_realm" ] || [ "$master_realm" == "null" ]; then
        echo "WARNING: Could not fetch master realm, skipping security headers configuration."
        return
    fi

    # Set X-Frame-Options to SAMEORIGIN so the admin console's auth iframe works
    master_realm=$(echo "$master_realm" | jq '.browserSecurityHeaders.xFrameOptions = "SAMEORIGIN"')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/master" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$master_realm" > /dev/null

    echo "Master realm X-Frame-Options set to SAMEORIGIN."
}

# --- Main ---
echo "=== Keycloak IdP Configuration ==="
if [ "${SKIP_KEYCLOAK_WAIT:-false}" == "true" ]; then
    echo "Skipping health check wait (SKIP_KEYCLOAK_WAIT=true)."
else
    wait_for_keycloak
fi
get_admin_token
configure_master_realm_security_headers
configure_login_gov_signing_key
configure_login_gov_acr_values
echo "=== IdP configuration complete ==="
