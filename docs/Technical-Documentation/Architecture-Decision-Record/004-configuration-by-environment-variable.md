# 4. Configuration by Environment Variable
Date: 2020-08-04 (Updated 2021-12-20)

## Status

Accepted

## Context

Applications need to be configured differently depending on where they are running. For example, the backend running locally will have different configuration then the backend running in production.

Further, environment variables can be designated "secret" or not; the term "secret key" is often used in place of secret environment variables. Secret keys are sometimes (but not always) shared between different deployment environments, which makes it useful to have a central "single source of truth" where a secret key can be kept and copied out to different environments. CircleCI solves this use case for us, allowing secret keys to be managed by the project's Environment Variables, and accessed in the deployment process to write to cloud.gov applications.

## Decision

We will use environment variables to configure applications. We will use Environment Variables in CircleCI to store and manage secret keys.

## Consequences

Using environment variables allows us to easily configure applications consistently. There is good support in cloud.gov for configuration via environment variables. Also the frontend will be easy to configure because there are frontend libraries that allow setting of environment variables with .env files.

## Notes