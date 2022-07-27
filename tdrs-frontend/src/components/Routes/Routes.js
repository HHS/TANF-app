import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import Profile from '../Profile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Reports from '../Reports'
import { useSelector } from 'react-redux'

import SiteMap from '../SiteMap'

import Home from '../Home'

/**
 * This component renders the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const AppRoutes = () => {
  // The logged in user in our Redux state
  const user = useSelector((state) => state.auth.user)

  const role = user?.roles
  const hasRole = Boolean(role?.length > 0)

  const userAccessRequestApproved = Boolean(user?.['access_request'])

  const homeTitle =
    userAccessRequestApproved && !hasRole
      ? 'Request Submitted'
      : 'Welcome to TDP'

  return (
    <Routes>
      <Route exact path="/" element={<SplashPage />} />
      <Route exact path="/login" element={<LoginCallback />} />
      <Route
        exact
        path="/home"
        element={
          <PrivateRoute title={homeTitle}>
            <Home />
          </PrivateRoute>
        }
      />
      <Route
        exact
        path="/data-files"
        element={
          <PrivateRoute title="TANF Data Files">
            <Reports />
          </PrivateRoute>
        }
      />

      <Route
        exact
        path="/site-map"
        element={
          <PrivateRoute title="Site Map">
            <SiteMap user={user} />
          </PrivateRoute>
        }
      />
      <Route
        exact
        path="/profile"
        element={
          <PrivateRoute title="Profile">
            <Profile />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<NoMatch />} />
    </Routes>
  )
}

export default AppRoutes
