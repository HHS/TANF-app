import React from 'react'
import { Switch, Route } from 'react-router-dom'
import SplashPage from '../SplashPage/SplashPage'
import Dashboard from '../Dashboard'
// import EditProfile from '../EditProfile'
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
        <SplashPage />
      </Route>
      <Route exact path="/login">
        <LoginCallback />
      </Route>
      <PrivateRoute exact path="/dashboard">
        <Dashboard />
      </PrivateRoute>
      {/* <PrivateRoute exact path="/edit-profile">
        <EditProfile />
      </PrivateRoute> */}
    </Switch>
  )
}

export default Routes
