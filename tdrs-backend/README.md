# raft-tdp-main

Backend API Service for TDP. Deployed to Cloud.gov at https://tdp-backend.app.cloud.gov/ .

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  
- [Login.gov Account](https://login.gov/)
- [Cloud.gov Account](https://cloud.gov/)
- [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html)

# Contents

- [Local Development Options](#Local-Development-Options)
- [Code Unit Test, Linting Test, and Vulnerability Scan](#Code-Unit-Test,-Linting-Test,-and-Vulnerability-Scan)
- [Manual Cloud.gov Deployments](#Manual-Cloud.gov-Deployments)

# Testing the Local Backend Service:

  **Login is dependent on the [tdrs-frontend](../tdrs-frontend/README.md) service. You will need a local instance of that application running.**
  
This project uses a Pipfile for dependency management.

### Local Development Options

**Commands are to be executed from within the `tdrs-backend` directory**

1.) Configure your local environment by copying over the .env.example file
```bash
$ cp .env.example .env
```

2.) Replace secrets in `.env` with actual values. To obtain the correct values, 
please pull from [cloud.gov](https://cloud.gov) or contact the Product Manager.

3.) For Django Admin access, replace the value for `DJANGO_SU_NAME` in `.env` 
with the email you use to login to [login.gov](https://login.gov)

4.) Start the backend via docker-compose: 

```bash
# Merge in local overrides for docker-compose by using -f flag and specifying both
# This allows environment variables to be passed in from .env files locally.
$ docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build -d
```

This command will start the following containers: 

```bash
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS                            PORTS                    NAMES
c803336c1f61        tdp                          "bash -c 'python wai…"   3 seconds ago       Up 3 seconds                      0.0.0.0:8080->8080/tcp   tdrs-backend_web_1
20912a347e00        postgres:11.6                "docker-entrypoint.s…"   4 seconds ago       Up 3 seconds                      5432/tcp                 tdrs-backend_postgres_1
9c3e6c2a88b0        owasp/zap2docker-weekly      "sleep 3600"             4 seconds ago       Up 3 seconds (health: starting)                            tdrs-backend_zaproxy_1
a64c18db30ed        localstack/localstack:0.12.9 "docker-entrypoint.sh"   2 hours ago         Up 2 hours                        4571/tcp, 0.0.0.0:4566->4566/tcp, 8080/tcp   tdrs-backend_localstack_1
```

5.) The backend service will now be available via the following URL: `http://localhost:8080`

6.) To `exec` into the PostgreSQL database in the container. 

```bash
$ docker exec -it tdrs-backend_postgres_1 psql -U tdpuser -d tdrs_test
```

7.) For configuration of a superuser for admin tasks please refer to the [user_role_management.md](docs/user_role_management.md) guide. 

8.) Backend project tear down: 

```bash
 $ docker-compose down --remove-orphans
```

9.) The `postgres` and `localstack` containers use [Docker Named Volumes](https://spin.atomicobject.com/2019/07/11/docker-volumes-explained/) to persist container data between tear down and restart of containers. To clear all stored data and reset to an initial state, pass the `-v` flag when tearing down the containers:

```bash
 $ docker-compose down -v
```

----
### Environment Variable Inheritance
#### Local
When run locally with `docker-compose.local.yml` the following order of inheritance will be in place:
* Variables defined in `tdrs-backend/.env` file
* Variables defined directly in `docker-compose.yml`
* Defaults supplied in `tdrs-backend/tdpservice/settings/common.py` (Only **non secret** environment variables, do not commit defaults for any secrets!) 

#### CircleCI
When run within CI context the follow order of inheritance will define environment variables:
* For **secrets** only - Variables defined in CircleCI Project Settings (`JWT_KEY`, `JWT_CERT_TEST`, etc)
  * These must be manually passed in via docker-compose under the `environment` directive, ie. `MY_VAR=${MY_VAR}`
* Variables defined directly in `docker-compose.yml`
* Defaults supplied in `tdrs-backend/tdpservice/settings/common.py` (Only **non secret** environment variables, do not commit defaults for any secrets!) 

----
### Interfacing with AWS S3
This application supports simulating a fully functional AWS environment by use of the [localstack](https://github.com/localstack/localstack) project.

In order to abstract away implementation logic on when localstack should be used a `get_s3_client` function is exposed that handles determining when to
route to localstack vs a production AWS environment. This function is exposed globally to the app in `tdpservice/clients.py`.

This is controlled primarily via the environment variable `USE_LOCALSTACK` which gets set to True in local and CI environments.
Anywhere across the codebase that will reference S3 should use this function instead of boto3.client directly.

Example Usage:
```
from tdpservice.clients import get_s3_client

s3_client = get_s3_client()

s3_client.generate_presigned_url(**params)
```

----
### Code Unit Test, Linting Test, and Vulnerability Scan

1. Run local unit tests by executing the following command.

```bash
$ docker-compose run --rm web bash -c "./wait_for_services.sh && pytest"
```

2. Run local linting tests by executing the following command:

```bash
$ docker-compose run --rm web bash -c "flake8 ."
```

The [flake8](https://flake8.pycqa.org/en/latest/) linter is configured to check the formatting of the source against this [setup.cfg](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/tdrs-backend/setup.cfg#L20-L34) file. 

3. Run local penetration tests by executing the following shell script:

```bash
$ ./zap-scanner.sh
```

This will spin up a local instance of the backend service and execute a penetration test via open source tool [OWASP Zed Attack Proxy ](https://owasp.org/www-project-zap/).

----

### Cloud.gov Deployments:

Although CircleCi is [set up to auto deploy](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/.circleci/config.yml#L131) frontend and backend to Cloud.gov, if there is a need to do a manual deployment, the instructions below can be followed:

1.) Log into your cloud.gov account and set your space and organization:

```bash
$ cf login -a api.fr.cloud.gov --sso
$ cf target -o <ORG> -s <SPACE>
```

You may be prompted to select from a list of spaces under the selected organization. Please follow the prompt to select your intended deployment space


Example Prompt:
```
Targeted org hhs-acf-prototyping.

Select a space:
1. <SPACE-1>
2. <SPACE-2>

Space (enter to skip): 1
Targeted space <SPACE-1>.
```

2.) Push the image to Cloud.gov (you will need to be in the same directory as`tdrs-backend/manifest.yml`):

```bash
 $ cf push tdp-backend -f manifest.yml
```

**Steps 3 and 4 are reserved for deployments to new environments**


3.) You will then have to set all required environment variables via the cloud.gov GUI or the [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) via commands like the following:

 ```bash
 $ cf set-env tdp-backend JWT_KEY "$(cat key.pem)"
 ```
 
- **For the list of required environment variables please defer to the `.env.example` file

4.) After this step you will need to bind the application to a Postgres RDS service if it has not been bound already: 
```bash
$ cf bind-service tdp-backend tdp-db
```

- **If a Postgres Service does not exist, create it using `cf create-service aws-rds shared-psql tdp-db`**

5.) To apply this newly bound service or apply any changes made to environment variables you will need to restage the application:
```bash
$ cf restage tdp-backend
```
