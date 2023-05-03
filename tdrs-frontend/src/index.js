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

// call auth_check
const store = configureStore()
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


// delete this line