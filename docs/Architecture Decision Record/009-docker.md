# 8. Docker

Date:

## Status

## Context

Docker defines a format for bundling an application and all its dependencies into a single object called a container, offering a consistent environment regardless of the hosting environment. At the beginning of the project it was uncertain that cloud.gov would be used as the hosting environment, so using Docker mitigates challenges created by moving environments.

## Decision

We will use Docker as our virtualization platform.

## Consequences

Docker containers can be transferred to any Docker-enabled machine allowing for portable deployments across hosting platforms. These containers will be executed with the guarantee that the execution environment exposed to the application is the same in development, vendor staging, gov staging, and production regardless of the hosting environment.
