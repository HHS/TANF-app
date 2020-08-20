# TDRS Frontend

This project uses the U.S. Web Design System ([USWDS](https://designsystem.digital.gov/)) and in particular, [trussworks/react-uswds](https://github.com/trussworks/react-uswds)

## To build for deployment

- From `TANF-app/tdrs-frontend` run
  ```
  docker build -t adamcaron/tdrs-frontend .
  ```
- If you wish to run the build distribution locally:
  ```
  docker run -it -p 3000:80 --rm adamcaron/tdrs-frontend:latest
  ```
- Push the image to the remote repository on hub.docker.com:
  ```
  docker push adamcaron/tdrs-frontend:latest
  ```

## To run locally

- Clone this repository and
  ```
  cd TANF-app/tdrs-frontend
  ```

- Spin up date application with `docker-compose`
```
docker-compose up --build
```
- Build the Docker image locally with
  ```
  docker build --target localdev -t adamcaron/tdrs-frontend:local .
  ```
- Run the app:
  ```
  docker run -it -p 3000:3000 -v $PWD/src/:/home/node/app/src --rm adamcaron/tdrs-frontend:local yarn start
  ```

Navigate to [localhost:3000](localhost:3000) and you should see the app.

The `TANF-app/tdrs-frontend/src` directory is mounted into the container so changes to the source code, when saved, automatically update the contents of `/home/node/app/src` in the container. Restarting the container is not necessary during development and you should see changes update in the UI instantly.

### Code Linting and Formatting

The app is set up with [ESLint](https://eslint.org/) and [Prettier](https://prettier.io/), and follows the [Airbnb Style Guide](https://github.com/airbnb/javascript).

To run eslint locally:
```
yarn lint
```

If you use [VSCode](https://code.visualstudio.com/) as an [IDE](https://en.wikipedia.org/wiki/Integrated_development_environment), it will be helpful to add the extensions, [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) and [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode). These make it possible to catch lint errors as they occur, and even auto-fix style errors (with Prettier).

### Running Tests

This project uses [Jest](https://jestjs.io/) for unit tests and [Cypress](https://www.cypress.io/) for end-to-end (e2e) tests.

**Unit Tests with Jest**

Jest provides an interactive test consolde that's helpful for development. After running the following commands, you will see options to run all the tests, run only failing tests, run specific tests, and more.
- To run unit tests locally:
  ```
  yarn test
  ```
- To run unit tests with code coverage report:
  ```
  yarn test:cov
  ```
- To run unit tests as a CI environment would, which runs the tests once (without the interactive console):
  ```
  yarn test:ci
  ```

Another simple way to run only one test (focus on only one test at a time) is to change `it()` to `fit()`. You can skip tests by changing `it()` to `xit()`. [These](https://create-react-app.dev/docs/running-tests/#focusing-and-excluding-tests) can be used in addition to the [methods](https://jestjs.io/docs/en/api) Jest provides.

In addition to [Jest's matchers](https://jestjs.io/docs/en/expect), this project uses [enzyme-matchers](https://github.com/FormidableLabs/enzyme-matchers) to simplify tests and make them more readable. Enzyme matchers is integrated with Jest using the [`jest-enzyme` package](https://github.com/FormidableLabs/enzyme-matchers/blob/master/packages/jest-enzyme/README.md#assertions) which provides many useful assertions for testing React components.

**End-to-End Tests with Cypress**

It is required to run the application locally for Cypress to run, since it actually navigates to the URL and performs tests on the rendered UI.
Cypress requires that the application is running locally in order to perform its tests, since it navigates to the URL and performs tests on the rendered UI.
- Run the app (see docs [to run locally](#to-run-locally))
- Open the Cypress app:
  ```
  yarn cy:open
  ```
- The Cypress Test Runner immediately displays a list of Integration Tests. Click on one to run it, or run all tests.
- Alternatively the tests can all be run from the command line without the interactive browser window:
  ```
  yarn cy:run
  ```

The [Cypress guides](https://docs.cypress.io/guides/getting-started/writing-your-first-test.html#Add-a-test-file) are helpful.

----

## Create React App Documentation

_The following is the documentation for [Create React App](https://github.com/facebook/create-react-app). It is kept here as a baseline set of documentation for the foundation of the TDRS frontend. It is the default output of initializing the React app._

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

### `yarn build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify


## Cloud.gov Deployments:

1.) Build a tagged docker image against the the target github branch:

`cd tdrs-backend; docker build -t goraftdocker/tdp-backend:devtest . -f docker/Dockerfile.dev`

2.) Define the tagged within the manifest.yml found inside the the `tdrs-backend/` directory:

```
version: 1
applications:
- name: tdp-frontend
  memory: 512M
  instances: 1
  disk_quota: 512
  docker:
    image: goraftdocker/tdp-frontend:devtest
```

3.) Log into your cloud.gov account and set your space and organization:

```
cf login -a api.fr.cloud.gov --sso
cf target -o <ORG> -s <SPACE>
```

4.) Push the image to Cloud.gov ( please ensure you're in the same directory as the manifest.yml): 

`cd tdrs-backend; cf push tdp-frontend --docker-image goraftdocker/tdp-frontend:devtest`

5.) You will then have to set all required environment variables via the cloud.gov GUI or CF CLI

 `cf set-env tdp-backend JWT_KEY "$(cat test_wtf.txt)"`
 **For the list of required envrionment variables please defer to `tdrs-backend/tdpservice/settings/env_vars/.env.local`


6.) To apply this newly bound service you may have to restage:
`cf restage tdp-frontend`