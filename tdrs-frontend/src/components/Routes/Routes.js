import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import EditProfile from '../EditProfile'
import LoginCallback from '../LoginCallback'
import Request from '../Request'
import Reports from '../Reports'
import Welcome from '../Welcome'
import PrivateRoute from '../PrivateRoute'

/**
 * This component renders the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const AppRoutes = () => {
  return (
    <Routes>
      <Route exact path="/" element={<SplashPage />} />
      <Route exact path="/login" element={<LoginCallback />} />
      <Route
        exact
        path="/welcome"
        element={
          <PrivateRoute title="Welcome to TDP">
            <Welcome />
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
        path="/edit-profile"
        element={
          <PrivateRoute title="Request Access">
            <EditProfile />
          </PrivateRoute>
        }
      />
      <Route
        exact
        path="/request"
        element={
          <PrivateRoute title="Request Submitted">
            <Request />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<NoMatch />} />
    </Routes>
  )
}

export default AppRoutes
