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

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

const store = configureStore()
store.dispatch(fetchAuth())

// Start the mirage server to stub some backend endpoints when running locally
startMirage()

ReactDOM.render(
  <Provider store={store}>
    <Router history={history}>
      <App />
    </Router>
  </Provider>,
  document.getElementById('root')
)
