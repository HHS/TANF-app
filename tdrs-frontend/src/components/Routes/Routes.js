import React from 'react'
import { Switch, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import EditProfile from '../EditProfile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Request from '../Request'
import Reports from '../Reports'
import Welcome from '../Welcome'
import { useSelector } from 'react-redux'

/**
 * This component renders the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const Routes = () => {
  return (
    <Switch>
      <Route exact path="/">
        <SplashPage />
      </Route>
      <Route exact path="/login">
        <LoginCallback />
      </Route>
      <PrivateRoute exact title="Welcome to TDP" path="/welcome">
        <Welcome />
      </PrivateRoute>
      <PrivateRoute exact title="TANF Data Files" path="/data-files">
        <Reports />
      </PrivateRoute>
      <PrivateRoute exact title="Request Access" path="/edit-profile">
        <EditProfile />
      </PrivateRoute>
      <PrivateRoute exact title="Request Submitted" path="/request">
        <Request />
      </PrivateRoute>
      <Route path="*">
        <NoMatch />
      </Route>
    </Switch>
  )
}

export default Routes
