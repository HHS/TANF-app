
# Stage 0: Create the app directory, install dependencies, and copy in the source code
FROM node:16.13-alpine3.14 AS localdev

# Due to M1 issues found here, adding solution: 
# https://stackoverflow.com/questions/69983063/
RUN apk add chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

USER node


RUN mkdir /home/node/app/ && chown -R node:node /home/node/app
WORKDIR /home/node/app

# Copy package.json and run npm install before copying the rest of the app in
# to allow Docker to cache the npm layer to prevent unnecessary installations
# when code changes occur
COPY --chown=node:node package.json package-lock.json ./

# Disable npm audit
RUN npm set audit false
# Install npm packages directly from package-lock.json <https://docs.npmjs.com/cli/v8/commands/npm-ci>
RUN npm ci


COPY --chown=node:node . .

ENV SASS_PATH=node_modules:src
ENV PORT=80
EXPOSE 80

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
