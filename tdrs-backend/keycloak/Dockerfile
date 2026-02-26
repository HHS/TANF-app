FROM quay.io/keycloak/keycloak:26.0

# Install jq for configure-idps.sh (static binary, no package manager needed)
ADD --chmod=755 https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64 /usr/local/bin/jq

COPY realm-export.json /opt/keycloak/data/import/realm-export.json
COPY configure-idps.sh /opt/keycloak/configure-idps.sh

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
