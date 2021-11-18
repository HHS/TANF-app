import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'

import { ConnectedRouter as Router } from 'connected-react-router'
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

// call autch_check
const store = configureStore()
store.dispatch(fetchAuth())

// if (window.location.href.match(/https:\/\/.*\.app\.cloud\.gov/)) {
// }
// Start the mirage server to stub some backend endpoints when running locally

ReactDOM.render(
  <Provider store={store}>
    <Router history={history}>
      <App />
    </Router>
  </Provider>,
  document.getElementById('root')
)
