# TDRS Frontend

This project uses the U.S. Web Design System ([USWDS](https://designsystem.digital.gov/)) and in particular, [trussworks/react-uswds](https://github.com/trussworks/react-uswds)

## To run locally

- Clone this repository and
  ```
  cd TANF-app/tdrs-frontend
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

## To build for deployment

- From `TANF-app/tdrs-frontend` run
  ```
  docker build -t adamcaron/tdrs-frontend:build .
  ```
- If you wish to run the build distribution locally:
  ```
  docker run -it -p 3000:80 --rm adamcaron/tdrs-frontend:build
  ```
- Push the image to the remote repository on hub.docker.com:
  ```
  docker push adamcaron/tdrs-frontend:build
  ```

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
