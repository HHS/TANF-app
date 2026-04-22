#!/bin/bash
set -euo pipefail

# entrypoint.sh -- Starts Keycloak on a fixed internal port, then nginx on the
# externally-facing port. If either process dies, the container exits.
#
# Usage: entrypoint.sh <kc.sh args...>
#   Local:    entrypoint.sh start-dev --import-realm
#   Cloud.gov: entrypoint.sh start --import-realm --optimized

KEYCLOAK_INTERNAL_PORT=8081
KEYCLOAK_MANAGEMENT_PORT=9000
NGINX_PORT="${PORT:-8080}"

echo "=== Container entrypoint ==="
echo "  Nginx port:       ${NGINX_PORT}"
echo "  Keycloak port:    ${KEYCLOAK_INTERNAL_PORT}"
echo "  Management port:  ${KEYCLOAK_MANAGEMENT_PORT}"

# Generate nginx config from template
sed "s/LISTEN_PORT/${NGINX_PORT}/" /opt/keycloak/nginx.conf.template > /tmp/nginx.conf

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
