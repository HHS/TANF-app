ARG REGISTRY_OWNER=hhs
ARG BASE_TAG=v0.2.0

FROM ghcr.io/${REGISTRY_OWNER}/tdp-frontend-base:${BASE_TAG} AS localdev

# ---
# Stage 0: Copy source
COPY --chown=node:node . .

# ---
# Stage 1: Create a production build
FROM localdev AS build
RUN npm run build:development

# ---
# Stage 2: Serve over nginx (minimal production image)
FROM nginx:1.25-alpine AS nginx

# Copy only the built static files from build stage
COPY --from=build /home/node/app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx/local/default.conf.template /etc/nginx/default.conf.template
COPY nginx/local/locations.conf /etc/nginx/locations.conf
COPY nginx/src/503.html /usr/share/nginx/html/503_.html
COPY nginx/src/static/ /usr/share/nginx/html/static/

# Remove default nginx config and set up custom config in single layer
RUN rm -f /etc/nginx/conf.d/default.conf /etc/nginx/nginx.conf && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html
