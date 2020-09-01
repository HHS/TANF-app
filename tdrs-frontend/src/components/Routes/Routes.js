import React from 'react'
import { Switch, Route } from 'react-router-dom'
import Welcome from '../Welcome'
import Dashboard from '../Dashboard'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'

/**
 * This component renters the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const Routes = () => {
  return (
    <Switch>
      <Route exact path="/">
        <Welcome />
      </Route>
      <Route exact path="/login">
        <LoginCallback />
      </Route>
      <PrivateRoute exact path="/dashboard">
        <Dashboard />
      </PrivateRoute>
    </Switch>
  )
}

export default Routes
