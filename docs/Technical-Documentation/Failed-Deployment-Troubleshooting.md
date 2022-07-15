# Failed Deployment Flow Troubleshooting

Date: 2021-07-15

## Status

In Progress

## Context
In preparation for production-ready infrastructure, we wanted to create a living document guide for troubleshooting application failures that is developer/technician oriented.

## Table of Contents
TBD

## CircleCI failures
**Symptom:** I deployed new code (via merging) but the app in Cloud.gov didn't update and is still running old code.

Initially, we need to find the step where this failed. For your branch, go to CircleCI `https://www.circleci.com/pipelines/github/raft-tech/TANF-app?branch="name-of-your-branch"` and inspect the workflow which failed, likely `build-and-test`.

### `secrets-check`:
Check that these steps succeeded. If not, you can expand the steps which should give you a read out of the offending line from either script of git-secrets or truffle0-hpog.
### `test-backend`:
### `test-frontend`:
### `deploy-infrastructure-dev`:
### `deploy-dev`:

## Compilation/runtime failure
**Symptom:** I deployed new code and now the app in Cloud.gov is down/just shows a white screen.

So if the CircleCI jobs are all green, then the failure happened inside Cloud.gov.


### Check that all environment variables exist in the backend app.
### Check that all services, routes are bound.
You can reference the TDP diagram to find the relevant services [here](link TODO).

Routes for dev environments should only be `tdp-frontend.apps.cloud.gov`, `tdp-backend-prod.apps.cloud.gov`, and the clamav-rest route.
### Misc stacktrace in the log
If the app is crashed or still staging, you likely won't be able to use a rolling update per the CircleCI flow so we would need to run `deploy-backend.sh` manually with a rebuild strategy which typically requires double-checking the relevant services and binding new routes manually. To do so, you will need to export all relevant environment variables including the non-standard CF_SPACE variable in your local shell environment for the script to be able to set those environment variables. You can inspect the script for a list of default variables to be  expected.

