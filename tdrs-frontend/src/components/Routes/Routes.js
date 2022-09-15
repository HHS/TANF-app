import React from 'react'
import { Routes, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import Profile from '../Profile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Reports from '../Reports'
import Home from '../Home'
import { useSelector } from 'react-redux'
import { accountIsInReview } from '../../selectors/auth'

/**
 * This component renders the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const AppRoutes = () => {
  const userAccountInReview = useSelector(accountIsInReview)
  const homeTitle = userAccountInReview ? 'Request Submitted' : 'Welcome to TDP'

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
