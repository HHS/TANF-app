# 11. Implement Cloud.gov Buildpacks

Date: 2021-02-26 (_updated 2022-01-03_)

## Status

Accepted

## Context

Currently, our frontend and backend apps are running in Docker containers on Cloud.gov. The deployment process involves building the docker containers at [DockerHub](https://dockerhub.com). Because there is very little security documentation on DockerHub, the path to getting an ATO with this process would be very difficult. There are other options that may be easier to document, but none of them offer the benefits of buildpacks, which have already been Fed Ramped and documented.

## Decision

Our recommendation is to move to Cloud.gov buildpacks at this time. They are already Fed Ramped, [shift responsibility to Cloud.gov](https://cloud.gov/docs/technology/responsibilities/) and ensure tightened security.

## Consequences

**Benefits**
- Simplifies path to ATO
- Better assurance of security
- [Shifts responsibility to Cloud.gov](https://cloud.gov/docs/technology/responsibilities/)
- Dockerhub will no longer be needed
- Since containers won't be visible to the public in Dockerhub we limit the chances of exposing sensitive information (ie. "secret" env vars) within the containers

**Risks**
- Deploying with Docker containers ensures the application runs the same way in all environments. We will no longer have that assurance.
- There will need to be more emphasis on testing against environment(s) deployed in Cloud.gov to be sure our code works with in the build pack.
- Environments shifting to buildpacks may be unstable during transition
- If we shift away from Cloud.gov, we may need to explore using docker again as fedramped buildpacks may not be available

## Notes
- Docker containers will still need to be maintained for local development and CI/CD
- Docker containers will still need to be hardened for CI/CD
- **<details><summary>Steps for restaging for updated buildpacks**</summary> 
    As described in [#1045](https://github.com/raft-tech/TANF-app/issues/1045), cloud.gov will inform us that buildpack(s) we use have been updated to a newer version via e-mail to all users with 'developer' role. The e-mail provides specific CloudFoundry CLI steps needed but we have already captured our deployment strategy process/commands in scripts/deploy-backend.sh. Running that script is the preferred methodology. Presently, the e-mail does not provide any specifics about the update, just that there was an update.

    Below is the restaging process in full:

    ### Find version changes
    0. **DO NOT RESTAGE ENVIRONMENTS**
    1. Inspect relevant official changelog(s):
        * https://github.com/cloudfoundry/nginx-buildpack/blob/master/CHANGELOG
        * https://github.com/cloudfoundry/python-buildpack/blob/master/CHANGELOG
    2. On a new branch, update docs/Technical-Documentation/buildpack-changelog.md with information of the following format:

        ```
        ## Buildpacks Changelog
        - MM/DD/YYYY [name v#.#.##](link)
        - 07/13/2021 [python-buildpack v1.7.43](https://github.com/cloudfoundry/python-buildpack/releases/tag/v1.7.43)
        ```

    3. Still on this branch, increment the buildpack versions in our relevant manifest files (tdrs-*end/manifest.buildpack.yml). Please note the version syntax at the end: `[...].git#v1.2.3`
        ```
          buildpacks:
            - https://github.com/cloudfoundry/python-buildpack.git#v1.7.53
        ```
    4. Deploy this dev branch to a dev environment to ensure it will deploy successfully and without errors on startup.

    ### Open final PR for staging

    5. Open a pull request to `develop` and assign to Technical Lead
    6. Merging pull request shall trigger rolling deploy of the updated buildpack(s) to staging without downtime.
    7. As `develop` has been updated, buildpack updates will get merged into feature branches through our regular processes.
</details>
