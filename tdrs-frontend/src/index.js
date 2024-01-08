import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'

import { ReduxRouter as Router } from '@lagunovsky/redux-react-router'
import { Provider } from 'react-redux'

import configureStore, { history } from './configureStore'
import startMirage from './mirage'
import { fetchAuth } from './actions/auth'
import App from './App'

import 'uswds/dist/js/uswds'
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

ReactDOM.render(
  <Provider store={store}>
    <Router store={store} history={history}>
      <App />
    </Router>
  </Provider>,
  document.getElementById('root')
)

// expose store when run in Cypress
if (window.Cypress) {
  window.store = store
}
