# Use the following to build: docker buildx build -t ghcr.io/raft-tech/keycloak_26.5:latest -f Dockerfile . --platform linux/amd64,linux/arm64 --push

# Stage 1: nginx binary and non-system shared libraries.
FROM nginx:1.27 AS nginx-source
# Collect libs that aren't part of glibc (those are already in ubi-micro).
# Also exclude libcrypt — Debian's version requires glibc 2.36, but ubi-micro
# only has glibc 2.34. We grab a compatible libcrypt from UBI 9 instead.
RUN mkdir /nginx-libs && \
    ldd /usr/sbin/nginx | awk '/=>/{print $3}' | \
    grep -v -E '(libc\.so|libm\.so|libdl\.so|libpthread|librt\.so|libcrypt\.so|ld-linux)' | \
    while read lib; do cp -L "$lib" /nginx-libs/; done

# Stage 2: libcrypt.so.1 compatible with UBI 9's glibc 2.34.
# Debian nginx links against libcrypt.so.1, but UBI 9 only ships libcrypt.so.2.
# The libxcrypt-compat package provides a backwards-compatible libcrypt.so.1.
FROM registry.access.redhat.com/ubi9/ubi-minimal AS ubi-libs
RUN microdnf install -y libxcrypt-compat && \
    mkdir /ubi-libs && cp -L /usr/lib64/libcrypt.so.1* /ubi-libs/

FROM quay.io/keycloak/keycloak:26.5.5

USER root
# Copy nginx binary, Debian-compatible libs, and UBI-compatible libcrypt.
COPY --from=nginx-source /usr/sbin/nginx /usr/sbin/nginx
COPY --from=nginx-source /nginx-libs/ /usr/lib64/
COPY --from=ubi-libs /ubi-libs/ /usr/lib64/
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

# Health and metrics are served on the management port (9000) by default.
ENV KC_DB=postgres
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true
ENV KC_FEATURES=user-event-metrics
ENV KC_HTTP_METRICS_HISTOGRAMS_ENABLED=true
ENV KC_EVENT_METRICS_USER_ENABLED=true
ENV KC_EVENT_METRICS_USER_EVENTS=client_login,code_to_token,login,logout,refresh_token,token_exchange
ENV KC_EVENT_METRICS_USER_TAGS=realm,idp,clientId
RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT ["/opt/keycloak/entrypoint.sh"]
