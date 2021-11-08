# TDP Tech Deep Dive - Circle CI & Environment Vars

## Circle CI Workflows
* A set of rules for defining run order/conditions for a group of jobs
* Without filters a workflow will run on every commit
* We use filters within workflows to ensure certain jobs are only run on designated branches (this is a qasp testing step :))
* Such as deploy-infrastructure-staging and deploy-staging - which only run when the branch being committed to is `raft-tdp-main`
* The `requires` tag allows us to make sure a certain job has completed before moving to the next step in the workflow
* Additional vocab:
    * Commands: reusable steps for jobs
    * Executors: build environments used for jobs
    * Jobs: a collection of steps run on an executor
    * Orbs: reusable code that can be imported in to circle config - similar to pip packages, etc
* We currently have 5 workflows:
    * `build-and-test`: Runs jobs `secrets-check`, `test-frontend` and `test-backend` on every commit
    * `dev-deployment`: Deploys a PR to the dev space. Triggered by a GitHub action whenever one of the relevant deployment labels is assigned via an API call to Circle CI with the pipeline parameter `run_dev_deployment`.
    * `nightly`: Runs every night at UTC midnight and performs an OWASP scan against the staging site for both backend and frontend then stores the results in Django using a Cloud Foundry task.
    * `owasp-scan`: Runs an OWASP scan against the backend and frontend for a given PR. Triggered by a GitHub action whenever the `QASP Review` label is assigned via an API call to Circle CI with the pipeline parameter `run_owasp_scan`.
    * `staging-deployment`: Deploys the main branch to the staging space in Cloud.gov. Triggered via merges to the branch `raft-tdp-main`.

## How are environment variables supplied in CI?
We manually set some environment variables in the project settings for Circle CI. From there, they are used in several places:

### Within Circle CI project settings:
* `CF_ORG`: used to determine the org to deploy to in cloud.gov
* `CF_USERNAME_DEV`: the username of the cloud.gov service account for the dev space
* `CF_PASSWORD_DEV`: the password for the account above
* `CF_USERNAME_STAGING`: the username of the cloud.gov service account for the staging space
* `CF_PASSWORD_STAGING`: the password for the account above
* `CF_USERNAME_PROD` / `CF_PASSWORD_PROD` : service account for prod - only will be configured in HHS Circle CI

NOTE: These do not get copied to the Cloud.gov application

### set-backend-env-vars.sh
This script is called from deploy-backend during initial deployments and sets the following environment variables:
* `BASE_URL`: backend service URL - set dynamically from CGAPPNAME_BACKEND parameter to script which gets passed from the Circle CI job definition
* `DJANGO_SECRET_KEY`: a salt used in numerous Django cryptographic functions
* `FRONTEND_BASE_URL`: the URL of the React app, used for redirects during login
* `DJANGO_SETTINGS_MODULE`: The module path for Django settings to be used
* `DJANGO_CONFIGURATION`: The class name from the above module that will be used for settings

NOTE: These will get copied in to the Cloud.gov application

### Environment variables defined per settings module
These all have defaults set in their respective settings modules, but may be overridden by defining the environment variable on the Cloud.gov app
* `ACR_VALUES`: sets IAL or AAL level for Login.gov redirects - https://developers.login.gov/oidc/#request-parameters
* `CLIENT_ASSERTION_TYPE`: sets the type of token that gets returned for id_tokens (we always default to urn:ietf:params:oauth:client-assertion-type:jwt-bearer)
* `CLIENT_ID`: the identifier of our client app in Login.gov (same for dev and staging, different for prod)
* `DJANGO_SU_NAME`: The name of the initial user who will be created as superuser - defaults to Lauren Frohlich in all deployed contexts
* `OIDC_OP_AUTHORIZATION_ENDPOINT`: Login.gov auth URL
* `OIDC_OP_ISSUER`: the Login.gov IDP URL
* `OIDC_OP_JWKS_ENDPOINT`: the Login.gov JWK endpoint - used to retrieve a public key to verify tokens were signed by them
* `OIDC_OP_LOGOUT_ENDPOINT`: endpoint to log a user out from login.gov
* `OIDC_OP_TOKEN_ENDPOINT`: endpoint to redirect to to login/retrieve token
* `OIDC_RP_CLIENT_ID`: A duplicate of CLIENT_ID but also referred to in the code

## Frontend CI build process

### test-frontend
* Runs most steps directly on the machine executor, utilizing `yarn` commands defined in package.json
* The exception to the above is the zap scanner step - which runs the frontend via docker-compose, using the nginx target instead of the local dev target
* Major steps:
    * Run ESLint - ensures styling standards are followed
    * Run Pa11y - automated accessibility testing
    * Run Jest - unit tests for the React frontend
    * Upload code coverage - uses Codecov
    * Run Cypress - integration tests using Cypress to simulate the browser
    * Store Artifacts - stores Pa11y screenshots taken

### deploy-frontend
* Called as a step in the `deploy-cloud-dot-gov` command
* Runs directly on the machine executor
* Installs Node.JS v12.18 and all project dependencies
* Calls script `/scripts/deploy-frontend.sh`, which does the following:
    * Using cloud.gov application name as an input (`CGHOSTNAME_BACKEND`) it sets the environment variables needed to communicate with the Django backend:
        * `REACT_APP_BACKEND_HOST`
        * `REACT_APP_BACKEND_URL`
        * Only difference in values is whether `/v1` is at the end
    * Runs `yarn build` which generates the HTML needed to serve to end users
    * Copies in the nginx configuration for build packs
    * Uploads the build output to Cloud.gov using `cf push`
    * Creates and maps the frontend route

## Backend CI build process

### test-backend
* Runs on a machine executor and executes steps using Docker Compose.
* Major steps:
    * Build and Spin-up Django API Service (using docker-compose)
    * Run Python Linting Test (flake8)
    * Run Pytest Unit Tests
    * Upload code coverage - uses Codecov

### deploy-backend
* Called as a step in the `deploy-cloud-dot-gov` command
* Runs directly on the machine executor
* Calls script `/scripts/deploy-backend.sh`, which does the following:
    * Uploads the backend application to Cloud.gov using `cf push`
    * Creates and maps the backend route
    * Checks if the JWT_CERT has been generated and if not, creates a new one.
    * If DEPLOY_STRATEGY passed is `initial` or `rebuild` it will do the following:
        * Bind the backend application to the S3 and RDS services in Cloud.gov
        * Run `/scripts/set-backend-env-vars.sh` (detailed above)
        * Restage the application to make environment variable and bound services live.
