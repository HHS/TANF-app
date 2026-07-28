ARG NODE_VERSION=22-alpine

FROM node:${NODE_VERSION} AS base
WORKDIR /home/node/app
ENV NEXT_TELEMETRY_DISABLED=1
RUN chown -R node:node /home/node
USER node
COPY --chown=node:node package.json yarn.lock .yarnrc.yml ./

FROM base AS deps
RUN corepack prepare yarn@4.6.0 && \
    corepack yarn install --immutable

FROM deps AS localdev
COPY --chown=node:node . .
CMD ["corepack", "yarn", "dev", "--hostname", "0.0.0.0", "--port", "3000"]

FROM deps AS build
COPY --chown=node:node . .
RUN corepack yarn build

FROM node:${NODE_VERSION} AS runtime
WORKDIR /home/node/app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
RUN corepack prepare yarn@4.6.0 && \
    chown -R node:node /home/node
USER node
COPY --from=build --chown=node:node /home/node/app/.next ./.next
COPY --from=build --chown=node:node /home/node/app/public ./public
COPY --from=build --chown=node:node /home/node/app/package.json /home/node/app/yarn.lock /home/node/app/.yarnrc.yml ./
COPY --from=build --chown=node:node /home/node/app/next.config.ts ./next.config.ts
COPY --from=build --chown=node:node /home/node/app/node_modules ./node_modules
EXPOSE 3000
CMD ["corepack", "yarn", "start", "--hostname", "0.0.0.0", "--port", "3000"]
