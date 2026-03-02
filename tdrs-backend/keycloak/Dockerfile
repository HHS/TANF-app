# Use the following to build: docker buildx build -t ghcr.io/raft-tech/keycloak_26:latest -f Dockerfile . --platform linux/amd64,linux/arm64 --push

# Stage 1: Install nginx from UBI 9 minimal (has microdnf package manager).
# Keycloak's ubi-micro base has no package manager, so we copy the binary out.
FROM registry.access.redhat.com/ubi9/ubi-minimal AS nginx-builder
RUN microdnf install -y nginx && microdnf clean all
# Collect nginx-specific shared libs (exclude glibc/ld-linux which are already
# in the Keycloak ubi-micro base and must not be overwritten).
RUN mkdir /nginx-libs && \
    ldd /usr/sbin/nginx | awk '/=>/{print $3}' | \
    grep -v -E '(libc\.so|libm\.so|libdl\.so|libpthread|librt\.so|ld-linux)' | \
    while read lib; do cp -L "$lib" /nginx-libs/; done

FROM quay.io/keycloak/keycloak:26.0

USER root
# Copy nginx binary, modules, and non-system shared library dependencies.
COPY --from=nginx-builder /usr/sbin/nginx /usr/sbin/nginx
COPY --from=nginx-builder /usr/lib64/nginx/ /usr/lib64/nginx/
COPY --from=nginx-builder /nginx-libs/ /usr/lib64/
RUN mkdir -p /var/log/nginx /tmp/nginx_client_body /tmp/nginx_proxy /tmp/nginx_fastcgi /tmp/nginx_uwsgi /tmp/nginx_scgi && \
    chown -R 1000:0 /var/log/nginx /tmp/nginx_*
USER 1000

# Install jq and curl for configure-idps.sh (static binaries, no package manager needed)
ADD --chmod=755 https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64 /usr/local/bin/jq
ADD --chmod=755 https://github.com/moparisthebest/static-curl/releases/download/v8.7.1/curl-amd64 /usr/local/bin/curl

COPY realm-export.json /opt/keycloak/data/import/realm-export.json
COPY configure-idps.sh /opt/keycloak/configure-idps.sh
COPY nginx.conf /opt/keycloak/nginx.conf.template
COPY --chmod=755 entrypoint.sh /opt/keycloak/entrypoint.sh

# Build with health/metrics on the main HTTP port (not the separate management port).
# This is required for the entrypoint health check and cloud.gov routing.
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_LEGACY_OBSERVABILITY_INTERFACE=true
RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT ["/opt/keycloak/entrypoint.sh"]
