import React from 'react'
import { createRoot } from 'react-dom/client'
import axios from 'axios'

import { ReduxRouter as Router } from '@lagunovsky/redux-react-router'
import { Provider } from 'react-redux'

import { TracingInstrumentation } from '@grafana/faro-web-tracing'
import {
  initializeFaro,
  ReactIntegration,
  getWebInstrumentations,
  createReactRouterV6Options,
  FaroErrorBoundary,
  faro,
} from '@grafana/faro-react'

import {
  createRoutesFromChildren,
  matchRoutes,
  Routes,
  useLocation,
  useNavigationType,
} from 'react-router-dom'
import configureStore, { history } from './configureStore'
import startMirage from './mirage'
import { fetchAuth } from './actions/auth'
import App from './App'

import '@uswds/uswds'
import './index.scss'

if (
  !window.location.href.match(/https:\/\/.*\.app\.cloud\.gov/) &&
  (process.env.REACT_APP_USE_MIRAGE || process.env.REACT_APP_PA11Y_TEST)
) {
  // needs to be called before auth_check
  startMirage()
}
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

// Initialize FaroSDK
if (process.env.REACT_APP_ENABLE_RUM === 'true') {
  initializeFaro({
    url: process.env.REACT_APP_FARO_ENDPOINT,
    app: {
      name: 'tdp-frontend',
      version: process.env.REACT_APP_VERSION,
      environment: process.env.NODE_ENV,
    },
    // Set a reasonable sample rate to control data volume
    sessionSampleRate: 0.5,
    instrumentations: [
      // Load the default Web instrumentations
      ...getWebInstrumentations({ captureConsole: true }),
      // Trace API calls and other async operations
      new TracingInstrumentation(),
      // Add React-specific instrumentation
      new ReactIntegration({
        // Track components that take >50ms to render
        componentRenderThreshold: 50,
        router: createReactRouterV6Options({
          createRoutesFromChildren,
          matchRoutes,
          Routes,
          useLocation,
          useNavigationType,
        }),
      }),
    ],
    meta: {
      // Add any application-specific metadata here
      appType: 'TANF Data Portal',
      service_name: 'tdp-frontend',
    },
  })
}

function devLogin(devEmail) {
  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL
  axios
    .post(`${BACKEND_URL}/login/cypress`, {
      username: devEmail,
      token: 'local-cypress-token',
    })
    .then(function (response) {
      console.log(response)
    })
    .catch(function (error) {
      console.log(error)
    })
  store.dispatch({ type: 'SET_AUTH', payload: { devEmail } })
  console.log(`dispatched SET_AUTH(${devEmail})`)
}

// call auth_check
const store = configureStore()
if (process.env.REACT_APP_DEVAUTH && !store.getState().auth?.user) {
  devLogin(process.env.REACT_APP_DEVAUTH)
}
store.dispatch(fetchAuth())

// if (window.location.href.match(/https:\/\/.*\.app\.cloud\.gov/)) {
// }
// Start the mirage server to stub some backend endpoints when running locally

/* istanbul ignore next */
const ErrorProvider = ({ children }) => {
  return !faro || !faro.api ? (
    <>{children}</>
  ) : (
    <FaroErrorBoundary>{children}</FaroErrorBoundary>
  )
}

const container = document.getElementById('root')
const root = createRoot(container)
root.render(
  <Provider store={store}>
    <Router store={store} history={history}>
      <ErrorProvider>
        <App />
      </ErrorProvider>
    </Router>
  </Provider>
)

// expose store when run in Cypress
if (window.Cypress) {
  window.store = store
}
