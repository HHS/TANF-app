# Github Status Reporting Badges

## Status

There are six dynamic status reporting badges being included in the root README.md file to provide a quick view of the following Github branches:

- `https://github.com/HHS/TANF-app/tree/main` 

- `https://github.com/raft-tech/TANF-app/tree/raft-tdp-main`


The badges will report on the following criteria:

- Circle CI Build Status

- Frontend code coverage percentage as reported to codecov.io

- Backend code coverage percentage as reported to codecov.io

## Context

### Dynamic Badge Source References

- CircleCI Build Status
   - This badge is provided directly from CircleCi configured to point directly to the latest build results of that branch.
   
     Example:
     [![CircleCI-Dev](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main.svg?style=shield)](https://circleci.com/gh/raft-tech/TANF-app/tree/raft-tdp-main)

- Code Coverage percentage as reported to codecov.io will be the same process for the frontend and backend.
   - This badge is provided directly from codecode.io and will be tied to tags for frontend and backend reports that have been uploaded to its server.
   
     Example:
      [![Codecov-Backend-Dev](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main/graph/badge.svg?flag=dev-backend)](https://codecov.io/gh/raft-tech/TANF-app/branch/raft-tdp-main?flag=dev-backend)


## Decision

This was done to facilitate a quick view of the status of the default Github repositories.

## Consequences

Due to limitations imposed by Github and occasional slow server response times from GitHub, some badges might require a page refresh to load.

## Dependabot Security Analysis

Dependabot status badges have not yet been updated to work with GitHub Native Dependabot per [this open issue](https://github.com/dependabot/dependabot-core/issues/1912). In lieu of these badges links are provided to the Dependabot alerts page on raft-tech and the Security Advisories page on HHS.
