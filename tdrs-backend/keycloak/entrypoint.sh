#!/bin/bash
set -euo pipefail

# entrypoint.sh -- Starts Keycloak on a fixed internal port, then nginx on the
# externally-facing port. If either process dies, the container exits.
#
# Usage: entrypoint.sh <kc.sh args...>
#   Local:    entrypoint.sh start-dev
#   Cloud.gov: entrypoint.sh start --optimized

KEYCLOAK_INTERNAL_PORT=8081
KEYCLOAK_MANAGEMENT_PORT=9000
NGINX_PORT="${PORT:-8080}"

echo "=== Container entrypoint ==="
echo "  Nginx port:       ${NGINX_PORT}"
echo "  Keycloak port:    ${KEYCLOAK_INTERNAL_PORT}"
echo "  Management port:  ${KEYCLOAK_MANAGEMENT_PORT}"
echo "  Realm env:        ${DEPLOY_ENV:-local}"
echo "  Config import:    ${KEYCLOAK_CONFIG_IMPORT_ON_STARTUP:-false}"

# Generate nginx config from template
sed "s/LISTEN_PORT/${NGINX_PORT}/" /opt/keycloak/nginx.conf.template > /tmp/nginx.conf

# Copy the selected environment-specific realm import before Keycloak starts.
/opt/keycloak/select-realm-config.sh

# Start Keycloak in background
echo "Starting Keycloak: kc.sh $* --http-port=${KEYCLOAK_INTERNAL_PORT} --cache=local"
/opt/keycloak/bin/kc.sh "$@" --http-port=${KEYCLOAK_INTERNAL_PORT} --cache=local &
KC_PID=$!

# Wait for Keycloak to be ready before starting nginx
# Health endpoint is on the management port (9000), not the main HTTP port.
echo "Waiting for Keycloak at http://127.0.0.1:${KEYCLOAK_MANAGEMENT_PORT}/health/ready ..."
MAX_ATTEMPTS=90
ATTEMPT=0
until curl -sf "http://127.0.0.1:${KEYCLOAK_MANAGEMENT_PORT}/health/ready" > /dev/null 2>&1; do
    ATTEMPT=$((ATTEMPT + 1))
    if [ "$ATTEMPT" -ge "$MAX_ATTEMPTS" ]; then
        echo "ERROR: Keycloak did not become ready after ${MAX_ATTEMPTS} attempts"
        kill $KC_PID 2>/dev/null || true
        exit 1
    fi
    if ! kill -0 $KC_PID 2>/dev/null; then
        echo "ERROR: Keycloak process exited unexpectedly"
        wait $KC_PID 2>/dev/null || true
        exit 1
    fi
    sleep 2
done
echo "Keycloak is ready."

if [ "${KEYCLOAK_CONFIG_IMPORT_ON_STARTUP:-false}" == "true" ]; then
    echo "Running Keycloak config import..."
    export KEYCLOAK_URL="http://127.0.0.1:${KEYCLOAK_INTERNAL_PORT}"
    export KEYCLOAK_USER="${KEYCLOAK_ADMIN}"
    export KEYCLOAK_PASSWORD="${KEYCLOAK_ADMIN_PASSWORD}"
    export KEYCLOAK_AVAILABILITYCHECK_ENABLED="${KEYCLOAK_AVAILABILITYCHECK_ENABLED:-true}"
    export KEYCLOAK_AVAILABILITYCHECK_TIMEOUT="${KEYCLOAK_AVAILABILITYCHECK_TIMEOUT:-120s}"
    export IMPORT_FILES_LOCATIONS="${IMPORT_FILES_LOCATIONS:-/opt/keycloak/data/import/realm-export.json}"
    export IMPORT_VARSUBSTITUTION_ENABLED="${IMPORT_VARSUBSTITUTION_ENABLED:-true}"
    export IMPORT_VARSUBSTITUTION_NESTED="${IMPORT_VARSUBSTITUTION_NESTED:-true}"
    export IMPORT_CACHE_ENABLED="${IMPORT_CACHE_ENABLED:-false}"
    export KEYCLOAK_CONFIG_CLI_JAR="${KEYCLOAK_CONFIG_CLI_JAR:-/opt/keycloak/keycloak-config-cli.jar}"

    /opt/keycloak/normalize-login-gov-key.sh
    echo "Keycloak config import complete."
fi

# Start nginx
echo "Starting nginx on port ${NGINX_PORT}..."
nginx -c /tmp/nginx.conf -g "daemon off;" &
NGINX_PID=$!

echo "=== Both processes running (KC=${KC_PID}, nginx=${NGINX_PID}) ==="

# If either process dies, kill the other and exit
wait -n $KC_PID $NGINX_PID
EXIT_CODE=$?

echo "A process exited (code=${EXIT_CODE}). Shutting down..."
kill $KC_PID 2>/dev/null || true
kill $NGINX_PID 2>/dev/null || true
wait $KC_PID 2>/dev/null || true
wait $NGINX_PID 2>/dev/null || true
exit $EXIT_CODE
