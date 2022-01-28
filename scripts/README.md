# Scripts

The TANF app uses several scripts through its lifecycle. 
These don't all get used by or interacted with by us too often,
but some are mission critical during deployment and review of 
the application. When a developer is working on these scripts, 
they should update this documentation so future developers 
understand the role of the scripts.

# Table of Contents

+ [set-backend-env-vars.sh](./README.md#set-backend-env-varssh)
+ [copy-login-gov-keypair.sh](./README.md#copy-login-gov-keypairsh)
+ [deploy-backend.sh](./README.md#deploy-backendsh)
+ [deploy-frontend.sh](./README.md#deploy-frontendsh)
+ [deploy-infrastructure-dev.sh](./README.md#deploy-infrastructure-devsh)
+ [deploy-infrastructure-staging.sh](./README.md#deploy-infrastructure-stagingsh)
+ [sudo-check.sh](./README.md#sudo-checksh)
+ [cf-checks.sh](./README.md#cf-checkssh)
+ [docker-check.sh](./README.md#docker-checksh)
+ [docker-compose-check.sh](./README.md#docker-compose-checksh)
+ [git-secrets-check.sh](./README.md#git-secrets-checksh)
+ [trufflehog-check.sh](./README.md#trufflehog-checksh)
+ [codecov-check.sh](./README.md#codecov-checksh)
+ [localstack-setup.sh](./README.md#localstack-setupsh)
+ [zap-hook.py](./README.md#zap-hookpy)
+ [zap-scanner.sh](./README.md#zap-scannersh)


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

```bash
./scripts/deploy-backend.sh <strategy> <app-name>
./scripts/deploy-backend.sh rolling raft-review
```
### Arguments

```bash
# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
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
APP_NAME=${2}

### Description
Mostly for use in our CircleCI pipelines, this script ensures the desired codebase is deployed into a given Cloud.gov application space.

### Where it's used

`deploy-backend.sh` is used in [CircleCI config](../.circleci/config.yml)'s job `deploy-backend` which is used by `deploy-cloud-dot-gov` command. This script is primarily via in CircleCI but with CloudFoundry set up and logged in locally, this can also be used by a developer manually. Please also see our [CircleCI documentation](../docs/Technical-Documentation/circle-ci.md#deploy-backend).

## deploy-frontend.sh


### Usage

```
./scripts/deploy-frontend.sh <strategy> <app-name>
./scripts/deploy-frontend.sh rolling raft-review
```
### Arguments

```bash
DEPLOY_STRATEGY=${1}

# The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}
CGHOSTNAME_BACKEND=${3}

REACT_APP_BACKEND_HOST= #Environment Variable
REACT_APP_BACKEND_URL= #Environment Variable
```

### Description
Mostly for use in our CircleCI pipelines, this script ensures the desired codebase is deployed into a given Cloud.gov application space.

### Where it's used

`deploy-frontend.sh` is used in [CircleCI config](../.circleci/config.yml)'s job `deploy-frontend` which is used by `deploy-cloud-dot-gov` command. This script is primarily via in CircleCI but with CloudFoundry set up and logged in locally, this can also be used by a developer manually. Please also see our [CircleCI documentation](../docs/Technical-Documentation/circle-ci.md#deploy-frontend).

## deploy-infrastructure-dev.sh

### Usage

```
scripts/deploy-infrastructure-dev.sh
```

### Arguments

#### CF Service Keys

 CF_USERNAME_DEV
 CF_PASSWORD_DEV

### Description
This script will manually run CircleCI's job `deploy-infrastructure-dev` which deploys the default Terraform codebase to a desired Cloud.gov application name in the tanf-dev space. Please see [Terraform docs](../terraform/README.md) for more information.

Requires local client to have CloudFoundry and CircleCI CLI tools to be configured and logged in.

Requires installation of jq - https://stedolan.github.io/jq/download/

### Where it's used

We don't use this in CI, it is for manually running the CI step with the same name. It is a developer tool.

## deploy-infrastructure-staging.sh
### Usage
```
scripts/deploy-infrastructure-staging.sh
```

### Arguments

no args

### Description
Script runs our CircleCI job `deploy-infrastructure-staging` using your CloudFoundry login credentials; it expects that you had run `cf login --sso` prior. 
Requires installation of jq - https://stedolan.github.io/jq/download/

### Where it's used

We don't use this in CI, it is for manually running the CI step with the same name. It is a developer tool.

# "Check" scripts
## sudo-check.sh

<details>
<summary>Details</summary>
    
### usage
---
```
./scripts/sudo-check.sh
```
### Arguments
no args
### Description
This script installs the `sudo` command and all of its dependencies if it is not already present.

### Where it's used
sudo-check.sh is used in the sudo-check [CircleCI command](../.circleci/config.yml#L85)
</details>

## cf-checks.sh
<details>
<summary>Details</summary>
    
### usage
---
```bash
./scripts/cf-check.sh
```
---
### Arguments
no args

### Description
This script installs the CloudFoundry `cf` command and all of its dependencies if it is not already present.

### Where it's used 
cf-check.sh is used in the [CircleCI command cf-check](../.circleci/config.yml#L22)
</details>

## docker-check.sh

<details>
<summary>Details</summary>
    
### Usage
---
```bash
./scripts/docker-check.sh
```
---
    
### Arguments
no args

### Description
This script installs the docker ecosytem and all of its dependencies if it is not already present. This is used by our CircleCI CI/CD pipelines.

### Where it's used 
docker-check.sh does not appear to be used in automation.
</details>
    
## docker-compose-check.sh

<details>
<summary>Details</summary>
    
### Usage
---
```
./scripts/docker-compose-check.sh
```
---
    
### Arguments
no args

### Description
This script installs the `docker-compose` command and all of its dependencies if it is not already present. This is used by our CircleCI CI/CD pipelines.
### Where it's used 
docker-compose-check.sh is used in the [CircleCI config docker-compose-check command](../.circleci/config.yml#L28).
</details>

## git-secrets-check.sh
<details>
<summary>Details</summary>
    
### Usage
---
```
./scripts/git-secrets-check.sh
```
---
### Arguments

no args

### Description

This script ensures that no secrets have been committed to the TANF repo. We leverage [Awslab's git-secrets tool](https://github.com/awslabs/git-secrets.git) to scan code to be uploaded. Developers can set up a pre-commit hook locally so this scan will run before committing/pushing by checking the README on their github repo linked earlier.

### Where it's used 
git-secrets-check.sh is used in the [secrets-check command](../.circleci/config.yml#L329).
</details>

## trufflehog-check.sh

<details>
<summary>Details</summary>
    
### Usage
---
```bash
./scripts/trufflehog-check.sh <branch-target>
```
---
### Arguments

`branch-target` the branch name you want to check.

### Description

Installs truffleHog in a python virtual environment and gets the hash of the latest commit in the target branch.
Looks at all commits since the last merge into raft-tdp-main, and entropy checks on large git diffs. 
If there are issues, they will be listed then script will abort.

### Where it's used 
trufflehog-check.sh is also used in the [secrets-check command](../.circleci/config.yml#L329).
</details>

## codecov-check.sh
  
<details>
<summary>Details</summary>
    
### Usage
---
```bash
./scripts/codecov-check.sh
```
---
### Arguments
no args

### Description

Check if code cov is installed, and if it isn't, the script installs it, and checks the integrity of the binary.

### Where it's used 
codecov-check.sh is used in CircleCI `codecov-upload` [job](../.circleci/config.yml#L91).
</details>

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

### Where it's used
This is used in `../tdrs-backend/docker-compose.yml` to setup your local docker connections to AWS.
    
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

### Where it's used
This script is used inside of `zap-scanner.sh`. It is not used directly.
    
## zap-scanner.sh
### Usage
```bash
./zap-scanner.sh frontend local
```

### Arguments

```bash
TARGET=$1
```
TARGET is either frontend or backend.
    
```bash
ENVIRONMENT=$2
```
ENVIRONMENT is either local or nightly.
    
### Description
This script is an easy-to-use wrapper around the OWASP ZAP python script, detailed above, which runs security scans against the desired target.
    
### Where it's used
Our CircleCI job `nightly-owasp-scan` utilizes this script to scan our stable deployment in Cloud.gov staging space.

## deploy-live-comms.sh

### Usage

```bash
./deploy-live-comms.sh rolling tdp-live-comms
```

### Arguments

```bash
# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_LIVE_COMMS=${2}
```

### Description

Used to deploy the live-comms static file app

### Where it's used

Our CircleCI job `deploy-staging` uses this to deploy any changes made to the `live-comms` app
