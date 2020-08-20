import React from 'react'
import { Switch, Route, useHistory } from 'react-router-dom'
import Welcome from '../Welcome'
import Dashboard from '../Dashboard'
import Private from '../Private'

const Routes = () => {
  const history = useHistory()
  return (
    <Switch>
      <Private path="/dashboard" history={history}>
        <Dashboard />
      </Private>
      <Route path="/">
        <Welcome />
      </Route>
    </Switch>
  )
}

export default Routes
