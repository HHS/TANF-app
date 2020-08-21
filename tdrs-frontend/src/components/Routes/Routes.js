import React from 'react'
import { Switch, Route } from 'react-router-dom'
import Welcome from '../Welcome'
import Dashboard from '../Dashboard'
import Private from '../Private'
import LoginCallback from '../LoginCallback'

const Routes = () => {
  return (
    <Switch>
      <Route exact path="/">
        <Welcome />
      </Route>
      <Route exact path="/login">
        <LoginCallback />
      </Route>
      <Private exact path="/dashboard">
        <Dashboard />
      </Private>
    </Switch>
  )
}

export default Routes
