FROM quay.io/keycloak/keycloak:26.0

# Install jq and curl for configure-idps.sh (static binaries, no package manager needed)
ADD --chmod=755 https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64 /usr/local/bin/jq
ADD --chmod=755 https://github.com/moparisthebest/static-curl/releases/download/v8.7.1/curl-amd64 /usr/local/bin/curl

COPY realm-export.json /opt/keycloak/data/import/realm-export.json
COPY configure-idps.sh /opt/keycloak/configure-idps.sh

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
