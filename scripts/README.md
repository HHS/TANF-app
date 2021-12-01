# scripts

The TANF app uses several scripts through its lifecycle. 
These don't all get used by or interacted with by us too often,
but some are mission critical during deployment and review of 
the application. When a developer is working on these scripts, 
they should update this documentation so future developers 
understand the role of the scripts.

# set-backend-env-vars.sh 

## usage 

```bash

./scripts/set-backend-env-vars.sh CGAPPNAME_BACKEND CG_SPACE
./scripts/set-backend-env-vars.sh tdp-backend-raft tanf-dev
```

## args

`CGAPPNAME_BACKEND` the sub domain of the app you are trying to set up environment variables for, like
`tdp-backend-raft`
`CG_SPACE` the space the app you are trying to set up for exists in, like `tanf-dev`

[A full list](https://github.com/raft-tech/TANF-app/blob/c0c9423dcd4d9b87930eb655a74dd8f2701e3dcf/docs/Technical-Documentation/TDP-environments-README.md) of spaces and backends can be found here

## description

Determine the appropriate BASE_URL for the deployed instance based on the
provided Cloud.gov App Name
Use Shell Parameter Expansion to replace localhost in the URL
Dynamically generate a new `DJANGO_SECRET_KEY`
Dynamically set `DJANGO_CONFIGURATION` based on Cloud.gov Space

# sudo-check.sh

## usage

```
./scripts/sudo-check.sh

```

## Args

no args

## description
Used during ci/cd to check if the `sudo` command is present.
it installs it if it isn't.

# cf-checks.sh

## usage

```bash
./scripts/cf-check.sh
```

## Args

no args

## description
Used during ci/cd to check if the cf command is present, 
if its not, install it and all of its dependencies.


# docker-check.sh


## Usage

```bash
./scripts/docker-check.sh
```
## Args

no args

## Description

Used during ci/cd to check if docker is installed in the environment. 
It installs it if it is not.

# docker-compose-check.sh

Used during ci/cd to check if docker compose is installed in the environment. 
It installs it if it is not.

## Args

no args

# git-secrets-check.sh

## Usage

```
./scripts/git-secrets-check.sh
```

## Args

no args

## description

Used during CI/CD to ensure that no secrets have been committed to the repo
grep will return non-zero code if nothing found, failing the build


# trufflehog-check.sh

## Usage

```bash
./scripts/trufflehog-check.sh <branch-target>
```

## Args

`branch-target` the branch name you want to check.

## Description

Installs truffleHog in a python virtual environment and gets the hash of the latest commit in the target branch.
Looks at all commits since the last merge into raft-tdp-main, and entropy checks on large git diffs. 
If there are issues, they will be listed then script will abort.


# codecov-check.sh
  
## Usage

```bash
./scripts/codecov-check.sh
```

## Args

no args

## Description

Check if code cov is installed, and if it isn't, the script installs it, and checks the integrity of the binary.

# copy-login-gov-keypair.sh

## usage

```bash
./scripts/copy-login-gov-keypair.sh
```

## Description

Copies Login.gov JWT_KEY + JWT_CERT from one Cloud.gov application to another.

## Args

`SOURCE_APP` The app to copy keys from.
`DEST_APP` The app to copy keys to.

# deploy-backend.sh

## description

The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

The application name  defined via the manifest yml for the frontend
CGHOSTNAME_BACKEND=${2}


# deploy-frontend.sh

## Usage

```
./scripts/deploy-frontend.sh rolling raft-review
```
## Args

```bash

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

# The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}
```

# deploy-infrastructure-dev.sh

## Usage

```
```

## Args

no args

## Description

Requires installation of jq - https://stedolan.github.io/jq/download/


# deploy-infrastructure-staging.sh

## Description

Requires installation of jq - https://stedolan.github.io/jq/download/

## Args

no args

# localstack-setup.sh


## Usage

```
./scripts/localstack-setup.sh
```
Create the bucket used by the Django app
Enable object versioning on the bucket

## Args

no args

# zap-hook.py


## Usage

This script is used in an argument passed inside of `zap-scanner.sh`. It is not used directly

## Args

no args


## description

Python hook that can be used to disable ignored rules in ZAP scans.
This hook runs after the ZAP API has been successfully started.

This is needed to disable passive scanning rules which we have set to IGNORE
in the [ZAP configuration file](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/reports/zap.conf). Due to an unresolved issue with the scripts
the HTML report generated will still include ignored passive rules so this
allows us to ensure they never run and won't be present in the HTML report.

https://github.com/zaproxy/zaproxy/issues/6291#issuecomment-725947370
https://github.com/zaproxy/zaproxy/issues/5212

# zap-scanner.sh

## Usage 
```bash
./scripts/zap-scanner.py```

## Args

TARGET=$1
ENVIRONMENT=$2

## Description

Used to invoke zap during CI, sends path to zap-hook.py to zap command and executes scan
on the target environment.
