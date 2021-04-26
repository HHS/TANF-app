import React from 'react'
import { Switch, Route, useLocation } from 'react-router-dom'
import SplashPage from '../SplashPage'
import EditProfile from '../EditProfile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Request from '../Request'
import Reports from '../Reports'

/** This component renders a message signalling to the user that this
 * page does not exist.
 */
function NoMatch() {
  let location = useLocation()

  return (
    <div>
      <h3>
        No match for <code>{location.pathname}</code>
      </h3>
    </div>
  )
}

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
      <PrivateRoute exact title="Request Access" path="/edit-profile">
        <EditProfile />
      </PrivateRoute>
      <PrivateRoute exact title="Request Submitted" path="/request">
        <Request />
      </PrivateRoute>
      <PrivateRoute exact title="TANF Data Files" path="/data-files">
        <Reports />
      </PrivateRoute>
      <Route path="*">
        <NoMatch />
      </Route>
    </Switch>
  )
}

export default Routes
