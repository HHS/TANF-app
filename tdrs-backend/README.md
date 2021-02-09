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
  
This project uses a Pipfile for dependency management. However, due to the limitations of the [Snyk Github Integration Supported Files](https://support.snyk.io/hc/en-us/articles/360000911957-Language-support) we must continue to support a requirements.txt for the time being.

  
### Local Development Options

**Commands are to be executed from within the `tdrs-backend` directory**

1.) Configure your local environment by copying over the .env.example file
```bash
$ cp .env.example .env
```

2.) Replace secrets in .env with actual values. To obtain the correct values, please contact the Product Manager.

3.) Start the backend via docker-compose: 

```bash
# Merge in local overrides for docker-compose by using -f flag and specifying both
# This allows environment variables to be passed in from .env files locally.
$ docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d
```

This command will start the following containers: 

```bash
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS                            PORTS                    NAMES
c803336c1f61        tdp                          "bash -c 'python wai…"   3 seconds ago       Up 3 seconds                      0.0.0.0:8080->8080/tcp   tdrs-backend_web_1
20912a347e00        postgres:11.6                "docker-entrypoint.s…"   4 seconds ago       Up 3 seconds                      5432/tcp                 tdrs-backend_postgres_1
9c3e6c2a88b0        owasp/zap2docker-weekly      "sleep 3600"             4 seconds ago       Up 3 seconds (health: starting)                            tdrs-backend_zaproxy_1
```

4.) The backend service will now be available via the following URL: `http://localhost:8080`

5.) To `exec` into the PostgreSQL database in the container. 

```bash
$ docker exec -it tdrs-backend_postgres_1 psql -U tdpuser -d tdrs_test
```

6.) For configuration of a superuser for admin tasks please refer to the [user_role_management.md](docs/user_role_management.md) guide. 

7.) Backend project tear down: 

```bash
 $ docker-compose down --remove-orphans
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
### Code Unit Test, Linting Test, and Vulnerability Scan

1. Run local unit tests by executing the following command.

```bash
$ docker-compose run web sh -c "pytest"
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


1.) Build and push a tagged docker image while on the the target Github branch:

```bash
$ docker build -t lfrohlich/tdp-backend:local . -f docker/Dockerfile.dev

$ docker push lfrohlich/tdp-backend:local
```


2.) Log into your cloud.gov account and set your space and organization:

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

3.) Push the image to Cloud.gov (you will need to be in the same directory as`tdrs-backend/manifest.yml`):

( **The `--var` parameter ingests a value into the ``((docker-frontend))`` environment variable in the manifest.yml**)

```bash
 $ cf push tdp-backend -f manifest.yml --var docker-backend=lfrohlich/tdp-backend:local
```

**Steps 4 and 5 are reserved for deployments to new environments**


4.) You will then have to set all required environment variables via the cloud.gov GUI or the [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html) via commands like the following:

 ```bash
 $ cf set-env tdp-backend JWT_KEY "$(cat key.pem)"
 ```
 
- **For the list of required environment variables please defer to the `.env.example` file

5.) After this step you will need to bind the application to a Postgres RDS service if it has not been bound already: 
```bash
$ cf bind-service tdp-backend tdp-db
```

- **If a Postgres Service does not exist, create it using `cf create-service aws-rds shared-psql tdp-db`**

6.) To apply this newly bound service or apply any changes made to environment variables you will need to restage the application:
```bash
$ cf restage tdp-backend
```
