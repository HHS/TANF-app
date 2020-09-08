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

# Testing the local Frontend Service:

  **Login is now dependent on the [tdrs-backend](../tdrs-backend/README.md) service. You will need a local instance of that application running.**


### Local Development Options

**Commands are to be executed from within the `tdrs-frontend` directory**

1.) Create a `env.local` file with the following command:
  ```
  cp .env.local.example .env.local
  ```
  - The `REACT_APP_BACKEND_URL` variable in this file points to the backend host. For local testing this value should default to the following :
  
   ```
   http://localhost:8080/v1
   ```


2.) Frontend project spin-up options: 

- Option 1 (Using Yarn directly): We recommend using [NVM](https://github.com/nvm-sh/nvm)

    ```bash
    $ nvm install 12.18.3 # Install specific node version
    $ yarn
    $ yarn build
    $ yarn start 
    ```

- Option 2 (Build and start via docker-compose):

    ```bash
    $ docker-compose up -d --build
    ```
    This will start one container named `tdrs-frontend_tdp-frontend` with port `3000`. Any changes made in `tdrs-frontend` folder will be picked up by docker automatically (no stop/run containers each time). 


3.) With the project started, you can access the landing page via a web-browser ( we recommend `Chrome`) at the following URL:
```
http://localhost:3000
```

4.) This will redirect you to the `TDP Homepage` page with a button labeled `Sign in with Login.gov`.

- Clicking this button will redirect you to the login.gov authentication page.
-  You must agree to associate your account with the `TANF Prototype: Development` application.
-  If you encounter any issues signing in, please ensure you are using a [Login.gov-Sandbox Account](https://idp.int.identitysandbox.gov/) and **NOT** your [Login.gov Account](login.gov).


5.) Upon successful authentication with you will be redirected to the frontend dashboard (`/dashboard`) UI with an option to sign out.


6.) Clicking the `Sign Out` button will log you out of the application and redirect you to the landing page,


7.) Frontend project tear down options: 

  - If using Option 1 or 3 from above:

    ```
     Kill the application running in your terminal.

     MacOS Example: control+c
    ```

  - Option 2 (If you ran the application via docker-compose):

    ```bash
    $ docker-compose down
    ```

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

Jest provides an interactive test consolde that's helpful for development. After running the following commands, you will see options to run all the tests, run only failing tests, run specific tests, and more.


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

### Manual Cloud.gov Deployments:

Although CircleCi is [set up to auto deploy](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/.circleci/config.yml#L131) frontend and backend to Cloud.gov, if there is a need to do a manual deployment, the instructions below can be followed:

1.) Build and push a tagged docker image while on the the target Github branch:

 (**Please note you need to be logged into docker for these operations**)

```
docker build -t goraftdocker/tdp-frontend:devtest . -f Dockerfile.dev`

docker push goraftdocker/tdp-frontend:devtest
```


2.) Log into your cloud.gov account and set your space and organization:

##### - **ORG: The target deployment organization as defined in cloud.gov Applications** 

##### - **SPACE: The target deployment space under the organization as defined in cloud.gov Applications**
```bash
$ cf login -a api.fr.cloud.gov --sso
$ cf target -o <ORG> -s <SPACE>
```

3.) Push the image to Cloud.gov (  you will need to be in the same directory as`tdrs-frontend/manifest.yml`):

( **The `--var` parameter ingests a value into the ``((docker-frontend))`` environment variable in the manifest.yml**)

```bash
 cf push tdp-frontend --no-route -f manifest.yml --var docker-frontend=goraftdocker/tdp-frontend:devtest
```

4.) It may be required to restage the application after deployment:

```bash
$ cf restage tdp-frontend
```