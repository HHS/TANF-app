# 11. Implement Cloud.gov Buildpacks

Date: 2021-02-26 (updated 2021-07-26)

## Status

Accepted

## Context

Currently, our frontend and backend apps are running in Docker containers on Cloud.gov. The deployment process involves building the docker containers at [DockerHub](https://dockerhub.com). Because there is very little security documentation on DockerHub, the path to getting an ATO with this process would be very difficult. There are other options that may be easier to document, but none of them offer the benefits of buildpacks, which have already been Fed Ramped and documented.

## Decision

Our recommendation is to move to Cloud.gov buildpacks at this time. They are already Fed Ramped, [shift responsibility to Cloud.gov](https://cloud.gov/docs/technology/responsibilities/) and ensure tightened security.

## Consequences

**Pros**

- Simplifies path to ATO
- Better assurance of security
- [Shifts responsibility to Cloud.gov](https://cloud.gov/docs/technology/responsibilities/)
- Dockerhub will no longer be needed
- Since containers won't be visible to the public in Dockerhub we limit the chances of exposing sensitive information (ie. "secret" env vars) within the containers

**Cons**
- Deploying with Docker containers ensures the application runs the same way in all environments. We will no longer have that assurance.
- There will need to be more emphasis on testing against environment(s) deployed in Cloud.gov to be sure our code works with in the build pack.
- Environments shifting to buildpacks may be unstable during transition
- If we shift away from Cloud.gov, we may need to explore using docker again as fedramped buildpacks may not be available

**Notes**
- Docker containers will still need to be maintained for local development and CI/CD
- Docker containers will still need to be hardened for CI/CD

## Restaging for updated buildpacks

As described in #1045, cloud.gov will inform us that buildpack(s) we use have been updated to a newer version via e-mail to all users with 'developer' role. The e-mail provides specific CloudFoundry CLI steps needed but we have already captured our deployment strategy process/commands in scripts/deploy-backend.sh. Running that script is the preferred methodology. Presently, the e-mail does not provide any specifics about the update, just that there was an update.

Below is the restaging process in full:
    1. Upon receipt of email from cloud.gov, restage against dev:
```bash
user@host$ cf login -a api.fr.cloud.gov --sso
API endpoint: api.fr.cloud.gov

Temporary Authentication Code ( Get one at https://login.fr.cloud.gov/passcode ): 
Authenticating...
OK


Targeted org hhs-acf-prototyping.

Select a space:
1. tanf-dev
2. tanf-staging

Space (enter to skip): 1
Targeted space tanf-dev.

API endpoint:   https://api.fr.cloud.gov
API version:    3.101.0
user:           abottoms@goraft.tech
org:            hhs-acf-prototyping
space:          tanf-dev 
$ cf restage tdp-backend-a11y
$ cf restage tdp-backend-raft
$ cf restage tdp-backend-qasp
$ cf restage tdp-backend-sandbox
OR
$ cf restage tdp-frontend-a11y
$ cf restage tdp-frontend-raft
$ cf restage tdp-frontend-qasp
$ cf restage tdp-frontend-sandbox

```
    1. Inspect dev environment in cloud.gov for new buildpack versions after restage
    1. Inspect relevant official changelog(s):
        * https://github.com/cloudfoundry/nginx-buildpack/blob/master/CHANGELOG
        * https://github.com/cloudfoundry/python-buildpack/blob/master/CHANGELOG
    1. On a new branch, update docs/Technical-Documentation/buildpack-changelog.md with information of the following format:
```
## Buildpacks Changelog
- MM/DD/YYYY [name v#.#.##](link)
- 07/13/2021 [python-buildpack v1.7.43](https://github.com/cloudfoundry/python-buildpack/releases/tag/v1.7.43)
```
    1. Open a pull request to 'raft-tdp-main' and assign to Technical Lead
    1. Merging pull request shall trigger rolling deploy of the updated buildpack(s) to staging & (eventually) prod without downtime

