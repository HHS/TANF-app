#!/bin/sh
# Creates Grafana orgs to match the deployed environment.
# Org 1 ("Main Org.") is created automatically by Grafana — renamed to "Admin".
# DIGIT org is created as ID 2 locally (ID 3 in deployed).
#
# Runs as a one-shot container after Grafana is healthy.

set -eu

GRAFANA_URL="${GRAFANA_URL:-http://grafana:9400}"
AUTH="admin:admin"

echo "Waiting for Grafana to be ready..."
i=0
while [ "$i" -lt 30 ]; do
    if curl -sf "${GRAFANA_URL}/api/health" > /dev/null 2>&1; then
        echo "Grafana is ready."
        break
    fi
    i=$((i + 1))
    if [ "$i" -eq 30 ]; then
        echo "ERROR: Grafana did not become ready in time."
        exit 1
    fi
    sleep 2
done

# Rename Org 1 from "Main Org." to "Admin"
echo "Renaming Org 1 to 'Admin'..."
curl -sf -X PUT "${GRAFANA_URL}/api/orgs/1" \
    -H "Content-Type: application/json" \
    -u "${AUTH}" \
    -d '{"name": "Admin"}'
echo ""

# Check if DIGIT org already exists
EXISTING=$(curl -sf "${GRAFANA_URL}/api/orgs/name/DIGIT" -u "${AUTH}" 2>/dev/null || echo "")
if echo "${EXISTING}" | grep -q '"id"'; then
    echo "DIGIT org already exists: ${EXISTING}"
else
    echo "Creating DIGIT org..."
    curl -sf -X POST "${GRAFANA_URL}/api/orgs" \
        -H "Content-Type: application/json" \
        -u "${AUTH}" \
        -d '{"name": "DIGIT"}'
    echo ""
fi

# Verify
echo ""
echo "Current orgs:"
curl -sf "${GRAFANA_URL}/api/orgs" -u "${AUTH}"
echo ""
echo "Done."
