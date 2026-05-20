#!/bin/bash
# configure-idps.sh
#
# Post-startup script to configure Keycloak identity providers with
# sensitive material that cannot be expressed in the checked-in realm JSON files:
#   - Login.gov RSA private key for private_key_jwt client authentication
#   - Login.gov acr_values authorization parameter
#   - tdp-django and tdp-grafana client redirect URIs and web origins
#
# Run this AFTER Keycloak has started and imported the realm.
# Prerequisites: curl, jq
#
# Environment variables:
#   KEYCLOAK_URL            - Keycloak base URL (default: http://localhost:8443)
#   KEYCLOAK_ADMIN          - Admin username (default: admin)
#   KEYCLOAK_ADMIN_PASSWORD - Admin password (default: admin)
#   DEPLOY_ENV              - Deployment environment: dev, staging, or prod.
#                             dev includes localhost redirect URIs; staging/prod do not.
#   LOGIN_GOV_JWT_KEY       - PEM or base64-encoded Login.gov private key
#   LOGIN_GOV_ACR_VALUES    - ACR values for Login.gov (default: IAL1)
#   KC_TDP_REDIRECT_URIS    - Comma-separated list of redirect URIs for the tdp-django client
#                             (e.g. https://tdp-frontend.app.cloud.gov/*)
#   KC_TDP_WEB_ORIGINS      - Comma-separated list of web origins for the tdp-django client
#                             (e.g. https://tdp-frontend.app.cloud.gov)
#   KC_CLI_REDIRECT_URI     - Additional redirect URI for the tdp-cli client
#                             (default: http://localhost/*)
#   KC_CLI_WEB_ORIGIN       - Additional web origin for the tdp-cli client
#                             (default: http://localhost)
#   SKIP_KEYCLOAK_WAIT      - Set to "true" to skip the health check wait
#                             (useful when running as a CF task after deploy)

set -euo pipefail

KEYCLOAK_MANAGEMENT_URL="${KEYCLOAK_MANAGEMENT_URL:-http://localhost:9001}"
KEYCLOAK_URL="${KEYCLOAK_URL:-http://localhost:8443}"
KEYCLOAK_ADMIN="${KEYCLOAK_ADMIN:-admin}"
KEYCLOAK_ADMIN_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
REALM="tdp"
DEPLOY_ENV="${DEPLOY_ENV:-dev}"
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
    local max_attempts=30
    local attempt=0
    local response=""

    echo "Obtaining admin token from ${KEYCLOAK_URL}..."

    until [ "$attempt" -ge "$max_attempts" ]; do
        attempt=$((attempt + 1))

        response=$(curl -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=${KEYCLOAK_ADMIN}" \
            -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
            -d "grant_type=password" \
            -d "client_id=admin-cli") || true

        TOKEN=$(echo "$response" | jq -r '.access_token // empty' 2>/dev/null || true)

        if [ -n "$TOKEN" ]; then
            echo "Admin token obtained."
            return
        fi

        echo "  Attempt ${attempt}/${max_attempts} - admin token endpoint not ready yet..."
        if [ -n "$response" ]; then
            echo "  Response: $response"
        fi
        sleep 2
    done

    echo "ERROR: Failed to obtain admin access token after ${max_attempts} attempts"
    if [ -n "$response" ]; then
        echo "Final response: $response"
    fi
    exit 1
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
    # Remove the masked clientSecret before PUT to avoid overwriting the real value.
    idp_config=$(echo "$idp_config" | jq --arg url "$new_url" \
        '.config.authorizationUrl = $url | del(.config.clientSecret)')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$idp_config" > /dev/null

    echo "Login.gov authorization URL updated with acr_values."
}

configure_login_gov_logout_params() {
    echo "Configuring Login.gov logout to send client_id instead of id_token_hint..."

    local idp_config
    idp_config=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}")

    if [ -z "$idp_config" ] || [ "$(echo "$idp_config" | jq -r '.alias')" == "null" ]; then
        echo "WARNING: Login.gov IdP not found, skipping logout param configuration."
        return
    fi

    local current_send_id_token
    current_send_id_token=$(echo "$idp_config" | jq -r '.config.sendIdTokenOnLogout // "true"')
    local current_send_client_id
    current_send_client_id=$(echo "$idp_config" | jq -r '.config.sendClientIdOnLogout // "false"')

    if [ "$current_send_id_token" == "false" ] && [ "$current_send_client_id" == "true" ]; then
        echo "Login.gov logout params already configured correctly."
        return
    fi

    # Login.gov requires client_id and does not accept id_token_hint on logout.
    # Remove the masked clientSecret before PUT to avoid overwriting the real value.
    idp_config=$(echo "$idp_config" | jq '
        .config.sendIdTokenOnLogout = "false" |
        .config.sendClientIdOnLogout = "true" |
        del(.config.clientSecret)')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$idp_config" > /dev/null

    echo "Login.gov logout configured: sendClientIdOnLogout=true, sendIdTokenOnLogout=false."
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

append_json_array_unique() {
    local array_json="$1"
    local value="$2"
    echo "$array_json" | jq --arg value "$value" 'if index($value) then . else . + [$value] end'
}

get_client_uuid() {
    local client_id="$1"
    kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients?clientId=${client_id}" \
        -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id // empty'
}

configure_tdp_cli_api_audience() {
    echo "Configuring tdp-cli client and Django API audience scope..."

    local scope_name="tdp-api-audience"
    local scope_id
    scope_id=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes?name=${scope_name}" \
        -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id // empty')

    local scope_json
    scope_json=$(jq -n \
        --arg name "$scope_name" \
        '{
            name: $name,
            description: "Adds the Django API audience to access tokens for external API clients.",
            protocol: "openid-connect",
            attributes: {
                "include.in.token.scope": "false",
                "display.on.consent.screen": "false"
            }
        }')

    if [ -z "$scope_id" ]; then
        kc_api -X POST "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$scope_json" > /dev/null
        scope_id=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes?name=${scope_name}" \
            -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id')
        echo "tdp-api-audience client scope created (${scope_id})."
    else
        scope_json=$(echo "$scope_json" | jq --arg id "$scope_id" '.id = $id')
        kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes/${scope_id}" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$scope_json" > /dev/null
        echo "tdp-api-audience client scope updated (${scope_id})."
    fi

    local mapper_json
    mapper_json=$(jq -n '{
        name: "tdp-django audience",
        protocol: "openid-connect",
        protocolMapper: "oidc-audience-mapper",
        consentRequired: false,
        config: {
            "included.client.audience": "tdp-django",
            "id.token.claim": "false",
            "access.token.claim": "true"
        }
    }')

    local mapper_id
    mapper_id=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes/${scope_id}/protocol-mappers/models" \
        -H "Authorization: Bearer ${TOKEN}" | jq -r 'map(select(.name == "tdp-django audience")) | first.id // empty')

    if [ -n "$mapper_id" ]; then
        mapper_json=$(echo "$mapper_json" | jq --arg id "$mapper_id" '.id = $id')
        kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes/${scope_id}/protocol-mappers/models/${mapper_id}" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$mapper_json" > /dev/null
        echo "tdp-django audience mapper updated (${mapper_id})."
    else
        kc_api -X POST "${KEYCLOAK_URL}/admin/realms/${REALM}/client-scopes/${scope_id}/protocol-mappers/models" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$mapper_json" > /dev/null
        echo "tdp-django audience mapper created."
    fi

    local redirect_uris='[]'
    local web_origins='[]'
    for uri in \
        "http://localhost/*" \
        "http://127.0.0.1/*" \
        "https://oauth.pstmn.io/v1/callback" \
        "${KC_CLI_REDIRECT_URI:-http://localhost/*}"; do
        redirect_uris=$(append_json_array_unique "$redirect_uris" "$uri")
    done
    for origin in \
        "http://localhost" \
        "http://127.0.0.1" \
        "${KC_CLI_WEB_ORIGIN:-http://localhost}"; do
        web_origins=$(append_json_array_unique "$web_origins" "$origin")
    done

    local cli_json
    cli_json=$(jq -n \
        --argjson redirect_uris "$redirect_uris" \
        --argjson web_origins "$web_origins" \
        '{
            clientId: "tdp-cli",
            name: "TDP CLI / Postman",
            description: "Public client for external API tools (Postman, CLI, CI). Authorization Code + PKCE and Device Authorization Grant; no client secret.",
            enabled: true,
            clientAuthenticatorType: "none",
            protocol: "openid-connect",
            publicClient: true,
            standardFlowEnabled: true,
            implicitFlowEnabled: false,
            directAccessGrantsEnabled: false,
            serviceAccountsEnabled: false,
            authorizationServicesEnabled: false,
            fullScopeAllowed: true,
            redirectUris: $redirect_uris,
            webOrigins: $web_origins,
            attributes: {
                "pkce.code.challenge.method": "S256",
                "oauth2.device.authorization.grant.enabled": "true",
                "post.logout.redirect.uris": "+"
            },
            defaultClientScopes: ["openid", "email", "profile", "tdp-user-attributes", "tdp-api-audience"],
            optionalClientScopes: []
        }')

    local cli_id
    cli_id=$(get_client_uuid "tdp-cli")
    if [ -z "$cli_id" ]; then
        kc_api -X POST "${KEYCLOAK_URL}/admin/realms/${REALM}/clients" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$cli_json" > /dev/null
        cli_id=$(get_client_uuid "tdp-cli")
        echo "tdp-cli client created (${cli_id})."
    else
        cli_json=$(echo "$cli_json" | jq --arg id "$cli_id" '.id = $id')
        kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${cli_id}" \
            -H "Authorization: Bearer ${TOKEN}" \
            -H "Content-Type: application/json" \
            -d "$cli_json" > /dev/null
        echo "tdp-cli client updated (${cli_id})."
    fi

    ensure_default_client_scope_attached "$cli_id" "$scope_id" "$scope_name"

    for client_id in "tdp-django" "tdp-grafana"; do
        local client_uuid
        client_uuid=$(get_client_uuid "$client_id")
        if [ -n "$client_uuid" ]; then
            ensure_default_client_scope_removed "$client_uuid" "$scope_id" "$scope_name" "$client_id"
        fi
    done

    echo "tdp-cli redirect URIs: $(echo "$redirect_uris" | jq -c .)"
    echo "tdp-cli web origins:   $(echo "$web_origins" | jq -c .)"
}

ensure_default_client_scope_attached() {
    local client_uuid="$1"
    local scope_id="$2"
    local scope_name="$3"
    local attached
    attached=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_uuid}/default-client-scopes" \
        -H "Authorization: Bearer ${TOKEN}" | jq --arg id "$scope_id" 'any(.[]; .id == $id)')

    if [ "$attached" == "true" ]; then
        echo "${scope_name} already attached to tdp-cli."
        return
    fi

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_uuid}/default-client-scopes/${scope_id}" \
        -H "Authorization: Bearer ${TOKEN}" > /dev/null
    echo "${scope_name} attached to tdp-cli."
}

ensure_default_client_scope_removed() {
    local client_uuid="$1"
    local scope_id="$2"
    local scope_name="$3"
    local client_id="$4"
    local attached
    attached=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_uuid}/default-client-scopes" \
        -H "Authorization: Bearer ${TOKEN}" | jq --arg id "$scope_id" 'any(.[]; .id == $id)')

    if [ "$attached" != "true" ]; then
        echo "${scope_name} not attached to ${client_id}; no removal needed."
        return
    fi

    kc_api -X DELETE "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_uuid}/default-client-scopes/${scope_id}" \
        -H "Authorization: Bearer ${TOKEN}" > /dev/null
    echo "${scope_name} removed from ${client_id}."
}

configure_tdp_client_urls() {
    echo "Configuring tdp-django client redirect URIs and web origins (env: ${DEPLOY_ENV})..."

    local client_id
    client_id=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients?clientId=tdp-django" \
        -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id')

    if [ -z "$client_id" ] || [ "$client_id" == "null" ]; then
        echo "WARNING: tdp-django client not found, skipping URL configuration."
        return
    fi

    local client_config
    client_config=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_id}" \
        -H "Authorization: Bearer ${TOKEN}")

    # Preserve current Keycloak values unless explicit replacement env vars are provided.
    local redirect_uris
    local web_origins
    redirect_uris=$(echo "$client_config" | jq '.redirectUris // []')
    web_origins=$(echo "$client_config" | jq '.webOrigins // []')

    if [ -n "${KC_TDP_REDIRECT_URIS:-}" ]; then
        redirect_uris='[]'
        IFS=',' read -ra uris <<< "$KC_TDP_REDIRECT_URIS"
        for uri in "${uris[@]}"; do
            uri=$(echo "$uri" | xargs)  # trim whitespace
            redirect_uris=$(append_json_array_unique "$redirect_uris" "$uri")
        done
    else
        echo "KC_TDP_REDIRECT_URIS not set; preserving existing tdp-django redirect URIs."
    fi

    if [ -n "${KC_TDP_WEB_ORIGINS:-}" ]; then
        web_origins='[]'
        IFS=',' read -ra origins <<< "$KC_TDP_WEB_ORIGINS"
        for origin in "${origins[@]}"; do
            origin=$(echo "$origin" | xargs)
            web_origins=$(append_json_array_unique "$web_origins" "$origin")
        done
    else
        echo "KC_TDP_WEB_ORIGINS not set; preserving existing tdp-django web origins."
    fi

    # For dev only: also allow localhost and 127.0.0.1 for local development.
    if [ "$DEPLOY_ENV" == "dev" ]; then
        for uri in \
            "http://localhost:3000/*" \
            "http://localhost:8080/*" \
            "http://localhost:8989/*" \
            "http://127.0.0.1:3000/*" \
            "http://127.0.0.1:8080/*" \
            "http://127.0.0.1:8989/*"; do
            redirect_uris=$(append_json_array_unique "$redirect_uris" "$uri")
        done

        for origin in \
            "http://localhost:3000" \
            "http://localhost:8080" \
            "http://localhost:8989" \
            "http://127.0.0.1:3000" \
            "http://127.0.0.1:8080" \
            "http://127.0.0.1:8989"; do
            web_origins=$(append_json_array_unique "$web_origins" "$origin")
        done
    fi

    client_config=$(echo "$client_config" | jq \
        --argjson redirect_uris "$redirect_uris" \
        --argjson web_origins "$web_origins" \
        '.redirectUris = $redirect_uris | .webOrigins = $web_origins')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_id}" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$client_config" > /dev/null

    echo "tdp-django redirect URIs: $(echo "$redirect_uris" | jq -c .)"
    echo "tdp-django web origins:   $(echo "$web_origins" | jq -c .)"
}

configure_grafana_client_urls() {
    if [ -z "${KC_GRAFANA_REDIRECT_URI:-}" ] && [ "$DEPLOY_ENV" != "dev" ]; then
        echo "WARNING: KC_GRAFANA_REDIRECT_URI not set for env '${DEPLOY_ENV}', skipping Grafana client URL configuration."
        return
    fi

    echo "Configuring tdp-grafana client redirect URIs and web origins (env: ${DEPLOY_ENV})..."

    local client_id
    client_id=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients?clientId=tdp-grafana" \
        -H "Authorization: Bearer ${TOKEN}" | jq -r '.[0].id')

    if [ -z "$client_id" ] || [ "$client_id" == "null" ]; then
        echo "WARNING: tdp-grafana client not found, skipping."
        return
    fi

    local client_config
    client_config=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_id}" \
        -H "Authorization: Bearer ${TOKEN}")

    local redirect_uris='[]'
    local web_origins='[]'
    local post_logout_uri=""

    if [ -n "${KC_GRAFANA_REDIRECT_URI:-}" ]; then
        redirect_uris=$(echo "$redirect_uris" | jq --arg v "$KC_GRAFANA_REDIRECT_URI" '. + [$v]')
    fi
    if [ -n "${KC_GRAFANA_WEB_ORIGIN:-}" ]; then
        web_origins=$(echo "$web_origins" | jq --arg v "$KC_GRAFANA_WEB_ORIGIN" '. + [$v]')
    fi
    if [ -n "${KC_GRAFANA_POST_LOGOUT_URI:-}" ]; then
        post_logout_uri="$KC_GRAFANA_POST_LOGOUT_URI"
    fi

    # For dev only: also include localhost Grafana.
    if [ "$DEPLOY_ENV" == "dev" ]; then
        redirect_uris=$(echo "$redirect_uris" | jq '. + ["http://localhost:9400/login/generic_oauth"]')
        web_origins=$(echo "$web_origins" | jq '. + ["http://localhost:9400"]')
        post_logout_uri="${post_logout_uri:+${post_logout_uri}##}http://localhost:9400/*"
    fi

    client_config=$(echo "$client_config" | jq \
        --argjson redirect_uris "$redirect_uris" \
        --argjson web_origins "$web_origins" \
        '.redirectUris = $redirect_uris | .webOrigins = $web_origins')

    if [ -n "$post_logout_uri" ]; then
        client_config=$(echo "$client_config" | jq \
            --arg v "$post_logout_uri" \
            '.attributes["post.logout.redirect.uris"] = $v')
    fi

    # Remove masked clientSecret before PUT to avoid overwriting the real value.
    client_config=$(echo "$client_config" | jq 'del(.secret)')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/clients/${client_id}" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$client_config" > /dev/null

    echo "tdp-grafana redirect URIs: $(echo "$redirect_uris" | jq -c .)"
    echo "tdp-grafana web origins:   $(echo "$web_origins" | jq -c .)"
}

show_login_gov_on_login_page() {
    echo "Showing Login.gov on Keycloak login page..."

    # CLI and Postman users authenticate through the public Keycloak login page,
    # so Login.gov must remain visible even though TDP frontend uses kc_idp_hint.
    local idp_config
    idp_config=$(kc_api "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}")

    if [ -z "$idp_config" ] || [ "$(echo "$idp_config" | jq -r '.alias')" == "null" ]; then
        echo "WARNING: Login.gov IdP not found, skipping."
        return
    fi

    local already_visible
    already_visible=$(echo "$idp_config" | jq -r '(.hideOnLogin // false) | not')

    if [ "$already_visible" == "true" ]; then
        echo "Login.gov already visible on login page."
        return
    fi

    # Remove the masked clientSecret before PUT to avoid overwriting the real value.
    # Keycloak's GET API returns secrets as "**********" and PUTting that back would
    # replace the actual secret with the literal masked string.
    idp_config=$(echo "$idp_config" | jq '.hideOnLogin = false | del(.config.clientSecret)')

    kc_api -X PUT "${KEYCLOAK_URL}/admin/realms/${REALM}/identity-provider/instances/login-gov" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d "$idp_config" > /dev/null

    echo "Login.gov visible on login page."
}

main() {
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
    configure_login_gov_logout_params
    show_login_gov_on_login_page
    configure_tdp_client_urls
    configure_tdp_cli_api_audience
    configure_grafana_client_urls
    echo "=== IdP configuration complete ==="
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
