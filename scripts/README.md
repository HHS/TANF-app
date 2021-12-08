# Scripts

The TANF app uses several scripts through its lifecycle. 
These don't all get used by or interacted with by us too often,
but some are mission critical during deployment and review of 
the application. When a developer is working on these scripts, 
they should update this documentation so future developers 
understand the role of the scripts.

# Interacting with Cloud.gov

## [set-backend-env-vars.sh](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/scripts/set-backend-env-vars.sh) 

### Usage 

```bash

./scripts/set-backend-env-vars.sh CGAPPNAME_BACKEND CG_SPACE
./scripts/set-backend-env-vars.sh tdp-backend-raft tanf-dev
```

### Arguments

* `CGAPPNAME_BACKEND`: the sub domain of the app you are trying to set up environment variables for
  * Example: `tdp-backend-raft`
* `CG_SPACE`: the space the app you are trying to set up for is deployed in.
  * Example: `tanf-dev`

[A full list](https://github.com/raft-tech/TANF-app/blob/c0c9423dcd4d9b87930eb655a74dd8f2701e3dcf/docs/Technical-Documentation/TDP-environments-README.md) of spaces and backends can be found here

### Description

Based on the provided arguments, set the appropriate environment variables on the app in Cloud.gov.

* Determines the appropriate BASE_URL for the deployed instance based on the
provided Cloud.gov App Name.
  * For example, if the app name is `tdp-backend-raft` the `BASE_URL` will get set to `https://tdp-backend-raft.app.cloud.gov/v1`.
  * If there is already an existing `BASE_URL` environment variable set, the script will use Shell Parameter Expansion to replace localhost in the URL to prevent any issues.
* Dynamically sets the `FRONTEND_BASE_URL` by replacing `backend` with `frontend` in the `BASE_URL` value.
* Dynamically generates a new `DJANGO_SECRET_KEY` for each deployment. This value is generated with a python call to the `secrets` library. It is a randomly generated URL safe token that is 50 bytes in length.
* Dynamically sets `DJANGO_CONFIGURATION` based on Cloud.gov Space.
  * `tanf-prod` space results in a Django configuration of `Production`.
  * `tanf-staging` uses the `Staging` configuration
  * All other spaces use the `Development` configuration
  * This refers to the Django settings class that will be used within the `tdpservice.settings.cloudgov` module. 

### Where it's used
The script `deploy-backend` invokes this script if the `DEPLOY_STRATEGY` is `initial`, `bind` or `rebuild`. Can optionally be run locally on its own.


## [copy-login-gov-keypair.sh](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/scripts/copy-login-gov-keypair.sh)

### Usage

```bash
./scripts/copy-login-gov-keypair.sh <source-app> <dest-app>
```

### Arguments

* `SOURCE_APP`: The app to copy keys from.
  * Example: `tdp-backend-raft`
* `DEST_APP`: The app to copy keys to.
  * Example: `tdp-backend-qasp`

### Description

Copies Login.gov JWT_KEY + JWT_CERT from one Cloud.gov application to another. This assumes that the user is already logged in to the Cloud Foundry CLI via the `cf login --sso` command. Both apps must exist within the same space.

### Where it's used

This script is only a convenience tool for developers, it has no direct usage in CI.


## deploy-backend.sh

### Usage

```
./scripts/deploy-backend.sh <strategy> <app-name>
./scripts/deploy-backend.sh rolling raft-review
```
### Arguments

The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

possible values:
+ rolling
    deploy to a new server leaving the existing one up until the deployment has succeeded

+ bind
    Bind the services the application depends on, update the environment
    variables and restage the app.

+ initial
    There is no app with this name, and the services need to be bound to it
    for it to work. the app will fail to start once, have the services bind,
    and then get restaged.

+ rebuild
    You want to redeploy the instance under the same name
    Delete the existing app (with out deleting the services)
    and perform the initial deployment strategy.

The application name  defined via the manifest yml for the frontend
CGHOSTNAME_BACKEND=${2}


## deploy-frontend.sh

### Usage

```
./scripts/deploy-frontend.sh rolling raft-review
```
### Arguments

DEPLOY_STRATEGY=${1}

The deployment strategy you wish to employ ( rolling update or setting up a new environment)

+ rolling
    deploy to a new server leaving the existing one up until the deployment has succeeded

The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}

## deploy-infrastructure-dev.sh

### Usage

```
scripts/deploy-infrastructure-dev.sh
```

### Arguments

no args

### Description

Requires installation of jq - https://stedolan.github.io/jq/download/


## deploy-infrastructure-staging.sh
### Usage
```
scripts/deploy-infrastructure-staging.sh
```

### Arguments

no args

### Description
Script runs our CircleCI job "deploy-infrastructure-staging" using your CloudFoundry login credentials; it expects that you had run `cf login --sso` prior. 
Requires installation of jq - https://stedolan.github.io/jq/download/



# "Check" scripts
## sudo-check.sh
### usage
```
./scripts/sudo-check.sh
```
### Arguments
no args
### Description
This script installs the `sudo` command and all of its dependencies if it is not already present.

## cf-checks.sh
### usage
```bash
./scripts/cf-check.sh
```

### Arguments
no args

### Description
This script installs the CloudFoundry `cf` command and all of its dependencies if it is not already present.


## docker-check.sh
### Usage
```bash
./scripts/docker-check.sh
```

### Arguments
no args

### Description
This script installs the docker ecosytem and all of its dependencies if it is not already present. This is used by our CircleCI CI/CD pipelines.

## docker-compose-check.sh
### Usage
```
./scripts/docker-compose-check.sh
```

### Arguments
no args

### Description
This script installs the `docker-compose` command and all of its dependencies if it is not already present. This is used by our CircleCI CI/CD pipelines.

## git-secrets-check.sh
### Usage
```
./scripts/git-secrets-check.sh
```

### Arguments

no args

### Description

This script ensures that no secrets have been committed to the TANF repo. We leverage [Awslab's git-secrets tool](https://github.com/awslabs/git-secrets.git) to scan code to be uploaded. Developers can set up a pre-commit hook locally so this scan will run before committing/pushing by checking the README on their github repo linked earlier.


## trufflehog-check.sh

### Usage

```bash
./scripts/trufflehog-check.sh <branch-target>
```

### Arguments

`branch-target` the branch name you want to check.

### Description

Installs truffleHog in a python virtual environment and gets the hash of the latest commit in the target branch.
Looks at all commits since the last merge into raft-tdp-main, and entropy checks on large git diffs. 
If there are issues, they will be listed then script will abort.


## codecov-check.sh
  
### Usage
```bash
./scripts/codecov-check.sh
```

### Arguments
no args

### Description

Check if code cov is installed, and if it isn't, the script installs it, and checks the integrity of the binary.



## localstack-setup.sh
### Usage
```
./scripts/localstack-setup.sh <bucket> <region>
```

### Arguments

bucket : Name of the localstack bucket you want to create
region : Name of the localstack region you want your new bucket to be placed in

### Description
Create the S3 bucket used by the Django app
Enable object versioning on the bucket

## zap-hook.py

### Usage

This script is used in an argument passed inside of `zap-scanner.sh`. It is not used directly.

### Arguments
no args


### Description

Python hook that can be used to disable ignored rules in ZAP scans.
This hook runs after the ZAP API has been successfully started.

This is needed to disable passive scanning rules which we have set to IGNORE
in the [ZAP configuration file](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/reports/zap.conf). Due to an unresolved issue with the scripts
the HTML report generated will still include ignored passive rules so this
allows us to ensure they never run and won't be present in the HTML report.

https://github.com/zaproxy/zaproxy/issues/6291#issuecomment-725947370
https://github.com/zaproxy/zaproxy/issues/5212

## zap-scanner.sh

### Usage
```bash
./scripts/zap-scanner.py backend nightly
./scripts/zap-scanner.py frontend nightly
./scripts/zap-scanner.py backend circleci
./scripts/zap-scanner.py frontend circleci
```

### Arguments

TARGET=$1
ENVIRONMENT=$2

### Description

Used to invoke zap during CI, sends path to zap-hook.py to zap command and executes scan
on the target environment.
