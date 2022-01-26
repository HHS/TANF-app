import React from 'react'
import { Switch, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import Profile from '../Profile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Reports from '../Reports'
import Home from '../Home'

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
      <PrivateRoute exact title="Welcome to TDP" path="/home">
        <Home />
      </PrivateRoute>
      <PrivateRoute exact title="TANF Data Files" path="/data-files">
        <Reports />
      </PrivateRoute>
      <PrivateRoute exact title="Request Access" path="/profile">
        <Profile />
      </PrivateRoute>
      <Route path="*">
        <NoMatch />
      </Route>
    </Switch>
  )
}

export default Routes
