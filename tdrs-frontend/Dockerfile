# ---
# Stage 0: Creae the app directory, install dependencies, and copy in the source code
FROM node:12.18-alpine3.12 AS localdev

RUN mkdir /home/node/app/ && chown -R node:node /home/node/app
WORKDIR /home/node/app
COPY --chown=node:node package.json yarn.lock ./
USER node
RUN yarn install && yarn cache clean
COPY --chown=node:node . .


# ---
# Stage 1: Create a production build
FROM localdev AS build
RUN yarn build


# ---
# Stage 2: Serve over nginx
FROM nginx:1.19-alpine

# Copy the build folder from react to the root of nginx (www)
COPY --from=build /home/node/app/build /usr/share/nginx/html

# To using react router
# it's necessary to overwrite the default nginx configurations:
# remove default nginx configuration file, replace with custom conf
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
