import React from 'react'
import ReactDOM from 'react-dom'
import axios from 'axios'

import { ConnectedRouter as Router } from 'connected-react-router'
import { Provider } from 'react-redux'

import configureStore, { history } from './configureStore'
import { fetchAuth } from './actions/auth'
import App from './App'

import 'uswds/dist/js/uswds'
import './index.scss'
import startMirage from './mirage'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

const store = configureStore()
store.dispatch(fetchAuth())
startMirage()

ReactDOM.render(
  <Provider store={store}>
    <Router history={history}>
      <App />
    </Router>
  </Provider>,
  document.getElementById('root')
)
