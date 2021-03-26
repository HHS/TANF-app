# Frontend for TDP

Frontend API Service for TDP. Deployed to Cloud.gov at https://tdp-frontend.app.cloud.gov/ . The project uses [USWDS](https://designsystem.digital.gov/) and in particular, [trussworks/react-uswds](https://github.com/trussworks/react-uswds)

# Prerequisites

- [Docker](https://docs.docker.com/docker-for-mac/install/)  
- [Login.gov Sandbox Account](https://idp.int.identitysandbox.gov/sign_up/enter_email)
- [Cloud.gov Account](https://cloud.gov/)
- [Cloud Foundry CLI](https://docs.cloudfoundry.org/cf-cli/install-go-cli.html)
- [Yarn JavaScript Package Manager](https://classic.yarnpkg.com/en/docs/install/#mac-stable) 

# Contents

- [Local Development Options](#Local-Development-Options)
- [Code Linting and Formatting](#Code-Linting-and-Formatting)
- [Unit and Integration Testing](#Unit-and-Integration-Testing)
- [Manual Cloud.gov Deployments](#Manual-Cloud.gov-Deployments)

# Running the Frontend locally:

  **Login is now dependent on the [tdrs-backend](../tdrs-backend/README.md#testing-the-local-backend-service) service. You will need a local instance of that application running.**

### Local Development:

Execute the command below from `tdrs-frontend/` folder to access the frontend at `http://localhost:3000`

```
$ docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build -d
```

The above command will bring up two docker containers

```
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS                            PORTS                    NAMES
7fa018dc68d1        owasp/zap2docker-stable      "sleep 3600"             4 seconds ago       Up 3 seconds (health: starting)   0.0.0.0:8090->8090/tcp   zap-scan
63f6da197629        tdrs-frontend_tdp-frontend   "/docker-entrypoint.…"   4 seconds ago       Up 3 seconds                      0.0.0.0:3000->80/tcp     tdp-ui
```

----
### Environment Variables
The TDP frontend utilizes built in Create React App (CRA) handling for environment variables which leverages multiple `.env` files:
* `.env`: Default.
* `.env.local`: Local overrides. This file is loaded for all environments except test.
* `.env.development`, `.env.test`, `.env.production`: Environment-specific settings.
* `.env.development.local`, `.env.test.local`, `.env.production.local`: Local overrides of environment-specific settings.

All of these `.env` files can be checked in to source control, with the exception of `.local` overrides and provided that they contain no *secrets*.

The order of inheritance for env files depends on how the application was built/launched.

#### Docker
When running this app with Docker on localhost React will assign `NODE_ENV=development` and use this inheritance order:
* .env.development.local
* .env.local
* .env.development
* .env

#### `npm start` / `yarn start`
When running this app directly on localhost React will assign `NODE_ENV=development` and use this inheritance order:
* Any variables set directly on host machine (ie. export MY_VAR=...)
* .env.development.local
* .env.local
* .env.development
* .env

#### `npm test` / `yarn test`
During tests, the env files are loaded in this order:
* .env.test.local
* .env.test
* .env

#### CircleCI
The current CircleCI config utilizes yarn to build and test the frontend application. As such it follows this order of inheritance for environment variables:
* Any variables set directly in CircleCI Project Settings
* .env.test.local
* .env.test
* .env

[See CRA documentation for more info](https://create-react-app.dev/docs/adding-custom-environment-variables/#adding-development-environment-variables-in-env)

----
### Code Linting and Formatting

The app is set up with [ESLint](https://eslint.org/) and [Prettier](https://prettier.io/), and follows the [Airbnb Style Guide](https://github.com/airbnb/javascript).

To run eslint locally:
```bash
$ yarn lint
```

If you use [VSCode](https://code.visualstudio.com/) as an [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment), it will be helpful to add the extensions, [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) and [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode). These make it possible to catch lint errors as they occur, and even auto-fix style errors (with Prettier).

----

### Unit and Integration Testing

This project uses [Jest](https://jestjs.io/) for unit tests and [Cypress](https://www.cypress.io/) for end-to-end (e2e) tests.

**Unit Tests with Jest**

Jest provides an interactive test console that's helpful for development. After running the following commands, you will see options to run all the tests, run only failing tests, run specific tests, and more.


1.) To run unit tests locally:
  ```bash
  $ yarn test
  ```
2.) To run unit tests with code coverage report:
  ```bash
  $ yarn test:cov
  ```
3.) To run unit tests as a continuous integration environment would, which runs the tests once (without the interactive console):
  ```bash
  $ yarn test:ci
  ```

After running either `test:cov` or `test:ci`, coverage details can be seen as HTML in the browser by running:
```bash
$ open coverage/lcov-report/index.html
```

In addition to [Jest's matchers](https://jestjs.io/docs/en/expect), this project uses [enzyme-matchers](https://github.com/FormidableLabs/enzyme-matchers) to simplify tests and make them more readable. Enzyme matchers is integrated with Jest using the [`jest-enzyme` package](https://github.com/FormidableLabs/enzyme-matchers/blob/master/packages/jest-enzyme/README.md#assertions) which provides many useful assertions for testing React components.

**End-to-End Tests with Cypress**

It is required to run the application locally for Cypress to run, since it actually navigates to the URL and performs tests on the rendered UI.
Cypress requires that the application is running locally in order to perform its tests, since it navigates to the URL and performs tests on the rendered UI.
- Run the app (see docs [to run locally](#to-run-locally))
- Open the Cypress app:
  ```bash
  $ yarn cy:open
  ```
- The Cypress Test Runner immediately displays a list of Integration Tests. Click on one to run it, or run all tests.
- Alternatively the tests can all be run from the command line without the interactive browser window:
  ```bash
  $ yarn cy:run
  ```

The [Cypress guides](https://docs.cypress.io/guides/getting-started/writing-your-first-test.html#Add-a-test-file) are helpful.

----

### Cloud.gov Deployments:

Although CircleCi is [set up to auto deploy](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/.circleci/config.yml#L131) frontend and backend to Cloud.gov, if there is a need to do a manual deployment, the instructions below can be followed:

1.) Build and push a tagged docker image while on the the target Github branch:

 (**Please note you need to be logged into docker for these operations**)

```
docker build -t lfrohlich/tdp-frontend:local . -f Dockerfile.dev

docker push lfrohlich/tdp-frontend:local
```


2.) Log into your cloud.gov account and set your space and organization:

##### - **ORG: The target deployment organization as defined in cloud.gov Applications** 

##### - **SPACE: The target deployment space under the organization as defined in cloud.gov Applications**
```bash
$ cf login -a api.fr.cloud.gov --sso
$ cf target -o <ORG> -s <SPACE-1>
```

You may be prompted to select from a list of spaces under the selected target. Please follow the prompt to select your intended deployment space


Example Prompt:
```
Targeted org hhs-acf-prototyping.

Select a space:
1. <SPACE-1>
2. <SPACE-2>

Space (enter to skip): 1
Targeted space <SPACE-1>.
```

3.) Push the image to Cloud.gov (  you will need to be in the same directory as`tdrs-frontend/manifest.yml`):

( **The `--var` parameter ingests a value into the ``((docker-frontend))`` environment variable in the manifest.yml**)

```bash
 cf push tdp-frontend -f manifest.yml --var docker-frontend=lfrohlich/tdp-frontend:local
```

4.) To apply any changes made to environment variables you will need to restage the application:

```bash
$ cf restage tdp-frontend
```
