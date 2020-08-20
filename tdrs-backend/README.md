# raft-tdp-main

Backend API Service TDP.

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  
- [Login.gov Account](https://login.gov/)

# Local Development

Configure your local environment variables via the file found in this path:

(default values have been pulled from: [Login.gov Developers Guide](https://developers.login.gov/oidc/))

```
TANF-app/tdrs-backend/tdpservice/settings/env_vars/.env.local
```

_Exceptions_:

- the `JWT_KEY` should be the private key used generate the client_assertion for the `/authorize` call to login.gov 
   - By default  this file is referencing a system environment variable. To prevent
- the `CLIENT_ID` has had the values unique to deployment environments obscured. Please populate this with the intended `Issuer` value found via the login.gov app management dashboard


To start a docker container local development( project root exists in `tdrs-backend/`):
```
cd tdrs-backend; docker-compose up --build
```

## Testing the  local API Service:

**_Login_**

1.) Via a web-browser ( we suggest using `Chrome`) enter the following URL:
```
http://localhost:8000/v1/login/oidc
```

2.) This will redirect you to the `login.gov` authentication page
    - You must a agree to associate your account with the `TANF Prototype: Development` application.

3.) Upon successful authentication with `login.gov` you'll be redirected to your local running service:
    - The response here will include your username and if you're a new/existing user

**_Logout_**

**Please note: If you attempt to logout without being logged in you will receive a 500 error**

1.) Via a web-browser ( we suggest using `Chrome`) enter the following URL:
```
http://localhost:8000/v1/logout/oidc
```

Run this command to tear down the docker container:
```
docker-compose down --remove-orphans
```
