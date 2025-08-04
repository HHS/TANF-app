import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import Profile from '../Profile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Reports, { FRAReports } from '../Reports'
import { useSelector } from 'react-redux'
import { accountIsInReview } from '../../selectors/auth'
import { faro, FaroRoutes } from '@grafana/faro-react'

import SiteMap from '../SiteMap'
import Home from '../Home'

/* istanbul ignore next */
const RouteProvider = ({ children }) => {
  return !faro || !faro.api ? (
    <Routes>{children}</Routes>
  ) : (
    <FaroRoutes>{children}</FaroRoutes>
  )
}

/**
 * This component renders the routes for the app.
 * Routes have the 'exact' prop, so the order of routes
 * does not matter.
 */
const AppRoutes = () => {
  const user = useSelector((state) => state.auth.user)

  const [isInEditMode, setIsInEditMode] = useState(false)
  const [editContext, setEditContext] = useState(null) // 'access request' or 'profile'
  //const userAccountInReview = useSelector(accountIsInReview)
  const userAccountInReview = true // TODO: using for testing

  const homeTitle = isInEditMode
    ? editContext === 'profile'
      ? 'Edit Profile'
      : 'Edit Access Request'
    : userAccountInReview
      ? 'Request Submitted'
      : 'Welcome to TDP'

  return (
    <RouteProvider>
      <Route exact path="/" element={<SplashPage />} />
      <Route exact path="/login" element={<LoginCallback />} />
      <Route
        exact
        path="/home"
        element={
          <PrivateRoute title={homeTitle}>
            <Home
              setInEditMode={(val) => {
                setEditContext('home')
                setIsInEditMode(val)
              }}
            />
          </PrivateRoute>
        }
      />
      <Route
        exact
        path="/data-files"
        element={
          <PrivateRoute
            title="TANF Data Files"
            subtitle="Participation, Characteristics, and Caseload reports"
            requiredPermissions={['view_datafile', 'add_datafile']}
            requiresApproval
          >
            <Reports />
          </PrivateRoute>
        }
      />
      <Route
        exact
        path="/fra-data-files"
        element={
          <PrivateRoute
            title="FRA Data Files"
            subtitle="Outcomes Reports as established by the Fiscal Responsibility Act (FRA)"
            requiredPermissions={[
              'view_datafile',
              'add_datafile',
              'has_fra_access',
            ]}
            requiresApproval
          >
            <FRAReports />
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
          <PrivateRoute
            title={editContext === 'profile' ? homeTitle : 'My Profile'}
          >
            <Profile
              isEditing={isInEditMode}
              onEdit={() => {
                setEditContext('profile')
                setIsInEditMode(true)
              }}
              onCancel={() => {
                setIsInEditMode(false)
                setEditContext(null)
              }}
            />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<NoMatch />} />
    </RouteProvider>
  )
}

export default AppRoutes
