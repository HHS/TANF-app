# 8. Docker

Date:

## Status

## Context

Docker defines a format for bundling an application and all its dependencies into a single object called a container.

## Decision

We will use Docker as our virtualization platform.

## Consequences

Docker containers can be transferred to any Docker-enabled machine allowing for portable deployments across hosting platforms. These containers will be executed with the guarantee that the execution environment exposed to the application is the same in development, staging, and production.
