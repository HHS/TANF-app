FROM quay.io/keycloak/keycloak:26.0

# Install jq and curl for configure-idps.sh (static binaries, no package manager needed)
ADD --chmod=755 https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64 /usr/local/bin/jq
ADD --chmod=755 https://github.com/moparisthebest/static-curl/releases/download/v8.7.1/curl-amd64 /usr/local/bin/curl

COPY realm-export.json /opt/keycloak/data/import/realm-export.json
COPY configure-idps.sh /opt/keycloak/configure-idps.sh

# Build with health/metrics on the main HTTP port (not the separate management port).
# This is required for cloud.gov where CF only routes to the app's main port.
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_LEGACY_OBSERVABILITY_INTERFACE=true
RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
