import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import NoMatch from '../NoMatch'
import SplashPage from '../SplashPage'
import Profile from '../Profile'
import PrivateRoute from '../PrivateRoute'
import LoginCallback from '../LoginCallback'
import Reports, { FRAReports } from '../Reports'
import FeedbackReports from '../FeedbackReports/FeedbackReports'
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
  const userAccountInReview = useSelector(accountIsInReview)

  const [isInEditMode, setIsInEditMode] = useState(false)

  const homeTitle = isInEditMode
    ? 'Edit Access Request'
    : userAccountInReview
      ? 'Request Submitted'
      : 'Welcome to TDP'

  const profileTitle = isInEditMode ? 'Edit Profile' : 'My Profile'

  const setEditState = (isEditing) => {
    setIsInEditMode(isEditing)
  }

  return (
    <RouteProvider>
      <Route exact path="/" element={<SplashPage />} />
      <Route exact path="/login" element={<LoginCallback />} />
      <Route
        exact
        path="/home"
        element={
          <PrivateRoute title={homeTitle}>
            <Home setInEditMode={setEditState} />
          </PrivateRoute>
        }
      />
      <Route
        exact
        path="/data-files/:fy?/:q?/:type?/:stt?/:tab?"
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
        path="/fra-data-files/:fy?/:q?/:type?/:stt?/:tab?"
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
        path="/feedback-reports"
        element={
          <PrivateRoute
            // TODO: add requiredPermissions for post on reports and report source
            title="Upload Feedback Reports"
            subtitle="TANF WPR, SSP WPR, TANF & SSP Combined, and Time Limit Reports"
            requiresApproval
          >
            <FeedbackReports />
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
          <PrivateRoute title={profileTitle}>
            <Profile
              isEditing={isInEditMode}
              onEdit={() => setEditState(true)}
              onCancel={() => setEditState(false)}
              type="profile"
              user={user}
              setInEditMode={setEditState}
            />
          </PrivateRoute>
        }
      />
      <Route path="*" element={<NoMatch />} />
    </RouteProvider>
  )
}

export default AppRoutes
