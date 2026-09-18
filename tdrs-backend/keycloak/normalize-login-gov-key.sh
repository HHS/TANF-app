#!/bin/sh
set -eu

if [ -z "${LOGIN_GOV_JWT_KEY:-}" ]; then
    echo "ERROR: LOGIN_GOV_JWT_KEY must be set to a base64-encoded PEM key." >&2
    exit 1
fi

if ! decoded_key="$(printf '%s' "$LOGIN_GOV_JWT_KEY" | tr -d '\r\n ' | base64 -d 2>/tmp/login-gov-key-decode.err)"; then
    echo "ERROR: LOGIN_GOV_JWT_KEY is not valid base64." >&2
    cat /tmp/login-gov-key-decode.err >&2 || true
    exit 1
fi

normalized_key="$(printf '%s' "$decoded_key" | sed 's/\\n/\
/g')"

if ! printf '%s' "$normalized_key" | grep -q "BEGIN .*PRIVATE KEY"; then
    echo "ERROR: decoded LOGIN_GOV_JWT_KEY does not look like a PEM private key." >&2
    exit 1
fi

LOGIN_GOV_JWT_KEY_PEM="$(
    printf '%s' "$normalized_key" |
        sed -e ':a' \
            -e 'N' \
            -e '$!ba' \
            -e 's/\\/\\\\/g' \
            -e 's/"/\\"/g' \
            -e 's/\n/\\n/g'
)"
export LOGIN_GOV_JWT_KEY_PEM

KEYCLOAK_CONFIG_CLI_JAR="${KEYCLOAK_CONFIG_CLI_JAR:-/app/keycloak-config-cli.jar}"
if [ ! -f "$KEYCLOAK_CONFIG_CLI_JAR" ] && [ -f /opt/keycloak/keycloak-config-cli.jar ]; then
    KEYCLOAK_CONFIG_CLI_JAR="/opt/keycloak/keycloak-config-cli.jar"
fi

exec java ${JAVA_OPTS:-} -jar "$KEYCLOAK_CONFIG_CLI_JAR" "$@"
