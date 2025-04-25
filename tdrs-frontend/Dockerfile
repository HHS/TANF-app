FROM elipe17/tdp-frontend-base:latest AS localdev

# ---
# Stage 0: Copy source
COPY --chown=node:node . .

# ---
# Stage 1: Create a production build
FROM localdev AS build
RUN npm run build:development

# ---
# Stage 2: Serve over nginx
FROM nginx:1.25-alpine AS nginx

# Copy the build folder (from the result of the Stage 1 "build" stage) to the root of nginx (www)
COPY --from=build /home/node/app/build /usr/share/nginx/html

# To using react router
# it's necessary to overwrite the default nginx configurations:
# remove default nginx configuration file, replace with custom conf
RUN rm /etc/nginx/conf.d/default.conf
RUN rm /etc/nginx/nginx.conf
COPY nginx/local/default.conf.template /etc/nginx/default.conf.template
COPY nginx/local/locations.conf /etc/nginx/locations.conf
#COPY nginx/local/under_maintenance.html /etc/nginx/under_maintenance.html
COPY nginx/src/503.html /usr/share/nginx/html/503_.html
COPY nginx/src/static/ /usr/share/nginx/html/static/

# Links this container to the rpo in GHCR
LABEL org.opencontainers.image.source=https://github.com/raft-tech/TANF-app
LABEL org.opencontainers.image.description="Frontend Service for TDP."
LABEL org.opencontainers.image.licenses=CC0-1.0
