# Failed Deployment Flow Troubleshooting

Date: 2021-07-15

## Status

Accepted

## Context
In preparation for production-ready infrastructure, we wanted to create a living document guide for troubleshooting application failures that is developer/technician oriented.

## Table of Contents
+ [CircleCI failures](./Failed-Deployment-Troubleshooting.md#circleci-failures)
+ [Runtime failures](./Failed-Deployment-Troubleshooting.md#compilationruntime-failure)
+ [App Connectivity issues](./Failed-Deployment-Troubleshooting.md#app-connectivity-issues)
+ [App roll-back](./Failed-Deployment-Troubleshooting.md#revision-rollback)

## CircleCI failures
**Symptom:** I deployed new code (via merging) but the app in Cloud.gov didn't update and is still running old code.

Initially, we need to find the step where this failed. For your branch, go to CircleCI `https://www.circleci.com/pipelines/github/raft-tech/TANF-app?branch="name-of-your-branch"` and inspect the workflow which failed, likely `build-and-test`.

### `secrets-check`:
These steps attempt to prevent developers from accidently committing secrets or hardcoded keys tot he repo. If not, you can expand the steps which should give you a read out of the offending line from either script of git-secrets or truffle-hog.
### `test-backend`:
These steps ensure the backend Django application passes basic unit tests, compilation, and linting.
### `test-frontend`:
These steps ensure the ReactJS application passes basic unit tests, compilation, and linting.
### `deploy-infrastructure-dev`:
These steps include the essential Terraform setup.
### `deploy-dev`:
These steps run through the commands needed to actually deploy this commit to the resulting app(s).

## Compilation/runtime failure
**Symptom:** I deployed new code and now the app in Cloud.gov is down/just shows a white screen.

So if the CircleCI jobs are all green, then the failure happened inside Cloud.gov. You can inspect the logs either via the UI or using `cf logs tdp-backend-<name> --recent`.


### Check that all environment variables exist in the backend app.
1. Run the following command to see env variables for the target application: `cf env tdp-backend-<target>|less`
2. Compare against other backend apps within cloud.gov to ensure the values are similar and that we are not missing any. You can also reference `deploy-backend.sh` for those that are set automatically.


### Check that all services, routes are bound.
You can reference the TDP diagram to find the relevant services [here](images/tdp-environments.png).

Routes for dev environments should only be `tdp-frontend-<target>.apps.cloud.gov`, `tdp-backend-<target>.apps.cloud.gov`, and the clamav-rest route.

### App Connectivity issues
This section covers what to do when internal apps cannot connect to each other (e.g., backend can't use clamav)
Using the logs via `cf logs tdp-backend-<name> --recent`, you can check for network connectivity issues like below:
```
09:38:02.638: [APP/PROC/WEB.0] [2022-07-18 13:38:02,637 DEBUG clients.py::__init__:L37 :  Set clamav endpoint_url as 'http://tanf-staging-clamav-rest.apps.internal:9000'
09:38:02.638: [APP/PROC/WEB.0] Set clamav endpoint_url as 'http://tanf-staging-clamav-rest.apps.internal:9000'
09:38:02.638: [APP/PROC/WEB.0] [2022-07-18 13:38:02,637 DEBUG clients.py::scan_file:L64 :  Initiating virus scan for file: test_Section1
09:38:02.638: [APP/PROC/WEB.0] Initiating virus scan for file: test_Section1
09:38:02.644: [APP/PROC/WEB.0] Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fd4a6cfb550>: Failed to establish a new connection: [Errno 111] Connection refused')': /
09:38:04.648: [APP/PROC/WEB.0] Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fd4a6cfb7f0>: Failed to establish a new connection: [Errno 111] Connection refused')': /
09:38:08.655: [APP/PROC/WEB.0] Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7fd4a6cfba00>: Failed to establish a new connection: [Errno 111] Connection refused')': /
```

In this instance, it is a connection issue between the staging backend and the respective clamav app. You can allow network access using the following command:

```
cf add-network-policy <source> <destination>
```
Learn more by running `cf add-network-policy --help`

### Misc stacktrace in the log
If the app is crashed or still staging, you likely won't be able to use a rolling update per the CircleCI flow so we would need to run `deploy-backend.sh` manually with a rebuild strategy which typically requires double-checking the relevant services and binding new routes manually. To do so, you will need to export all relevant environment variables in your local shell environment for the script to be able to set those environment variables. You can inspect the script for a list of default variables to be expected.

**NOTE:** This will delete the existing app and *should* rebind relevant services but this is something you should double-check for a crashed app.

```
export JWT_KEY.......
export DJANGO_SU_NAME=yourname@goraft.tech
export LOGGING_LEVEL=DEBUG
[...]
bash scripts/deploy-backend.sh rebuild tdp-backend-raft tanf-dev
```

## Revision Rollback

First we need to get list of revisions and select a stable revision id.
```cf revisions {app-name}```

Then use the last successful guid, we can populate this reversion command:
```
cf curl v3/deployments \        
-X POST \
-d '{
  "revision": {
    "guid": "{last stable guid from list above}"
  },
  "relationships": {
    "app": {
      "data": {
        "guid": "{current app guid}"
      }
    }
  }
}'```
