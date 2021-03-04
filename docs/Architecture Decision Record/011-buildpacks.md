# 11. Record architecture decisions

Date: 2021-02-26

## Status

Pending

## Context

Currently, our frontend and backend apps are running in Docker containers on Cloud.gov. The deployment process involves building the docker containers at [DockerHub](https://dockerhub.com). Because there is very little security documentation on DockerHub, the path to getting an ATO with this process would be very difficult. There are other options that may be easier to document, but none of them offer the benefits of buildpacks, which have already been Fed Ramped and documented.

## Decision

Our recommendation is to move to Cloud.gov buildpacks at this time. They are already Fed Ramped, shift responsibility to Cloud.gov and ensure tightened security.

## Consequences

**Pros**

- Simplifies path to ATO
- Better assurance of security
- Shifts responsibility to Cloud.gov
- Dockerhub will no longer be needed
- Since containers won't be visible to the public in Dockerhub we limit the chances of exposing sensitive information (ie. "secret" env vars) within the containers

**Cons**
- Deploying with Docker containers ensures the application runs the same way in all environments. We will no longer have that assurance.
- There will need to be more emphasis on testing against environment(s) deployed in Cloud.gov to be sure our code works with in the build pack.
- Environments shifting to buildpacks may be unstable during transition

**Notes**
- Docker containers will still need to be maintained for local development and CI/CD
- Docker containers will still need to be hardened for CI/CD
