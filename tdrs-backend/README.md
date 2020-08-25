# raft-tdp-main

Backend API Service TDP.

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  
- [Login.gov Account](https://login.gov/)
- [Cloud.gov Account](https://cloud.gov/)]
- [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html)

# Local Development

Configure your local environment variables via the file found in this path:

(default values have been pulled from: [Login.gov Developers Guide](https://developers.login.gov/oidc/))

`TANF-app/tdrs-backend/tdpservice/settings/env_vars/.env.local`

_Exceptions_:

- the `JWT_KEY` should be the private key used generate the client_assertion for the `/authorize` call to login.gov 
   - By default  this file is referencing a system environment variable. To prevent
- the `CLIENT_ID` has had the values unique to deployment environments obscured. Please populate this with the intended `Issuer` value found via the login.gov app management dashboard


To start a docker container local development( project root exists in `tdrs-backend/`):
```
cd tdrs-backend; docker-compose up --build
```

## Testing the local API Service:

**_Login_**

1.) Via a web-browser ( we suggest using `Chrome`) enter the following URL:
```
http://localhost:8080/v1/login/oidc
```

2.) This will redirect you to the `login.gov` authentication page
    - You must a agree to associate your account with the `TANF Prototype: Development` application.

3.) Upon successful authentication with `login.gov` you'll be redirected to your local running service:
    - The response here will include your username and if you're a new/existing user

**_Logout_**

**Please note: If you attempt to logout without being logged in you will receive a 500 error**

1.) Via a web-browser ( we suggest using `Chrome`) enter the following URL:
```
http://localhost:8080/v1/logout/oidc
```

Run this command to tear down the docker container:
```
docker-compose down --remove-orphans
```
## Manual Test Scripts:

- "Test: Execute Python Unit Tests:

`"cd tdrs-backend; docker-compose run tdp sh -c \"python manage.py test\"`

- Test: Execute Python Linting Test:

`"cd tdrs-backend; docker-compose run --rm tdp bash -c \"flake8 .\"`

- Test: Execute Python OWASP ZAP Vulnerability Scan:

`"cd tdrs-backend; ./zap-scanner.sh"`

## Cloud.gov Deployments:

1.) Build a tagged docker image against the the target github branch:

`cd tdrs-backend; docker build -t goraftdocker/tdp-backend:devtest . -f docker/Dockerfile.dev`

2.) Define the tagged within the manifest.yml found inside the the `tdrs-backend/` directory:

```
version: 1
applications:
- name: tdp-app
  memory: 512M
  instances: 1
  disk_quota: 2G
  docker:
    image: goraftdocker/tdp-backend:devtest
```

3.) Log into your cloud.gov account and set your space and organization:

```
cf login -a api.fr.cloud.gov --sso
cf target -o <ORG> -s <SPACE>
```


4.) Push the image to Cloud.gov ( please ensure you're in the same directory as the manifest.yml): 

`cd tdrs-backend; cf push tdp-backend --docker-image goraftdocker/tdp-backend:devtest`

5.) You will then have to set all required environment variables via the cloud.gov GUI or CF CLI

 `cf set-env tdp-backend JWT_KEY "$(cat test
 .txt)"`
 **For the list of required envrionment variables please defer to `tdrs-backend/tdpservice/settings/env_vars/.env.local`

5.) After this step you'll need to bind the application to a postgres RDS service ( if one does not exist you'll have to create one): 
`cf bind-service tdp-backend db-raft`

6.) To apply this newly bound service you may have to restage:
`cf restage tdp-backend`


