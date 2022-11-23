import React, { useEffect } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Alert'
import PrivateTemplate from '../PrivateTemplate'
import IdleTimer from '../IdleTimer/IdleTimer'
import PermissionGuard from '../PermissionGuard'

/**
 * @param {React.ReactNode} children - One or more React components to be
 * rendered if the user is authenticated
 * @param {string} title Page title passed in to PrivateTemplate
 * which is automatically passed via withRouter
 */
function PrivateRoute({
  children,
  title,
  requiredPermissions,
  requiresApproval,
}) {
  const authenticated = useSelector((state) => state.auth.authenticated)
  const authLoading = useSelector((state) => state.auth.loading)

  const navigate = useNavigate()
  const dispatch = useDispatch()

  useEffect(() => {
    if (!authenticated && !authLoading) {
      dispatch(setAlert({ heading: 'Please sign in first', type: ALERT_INFO }))
      navigate('/')
    }

    if (authLoading) {
      dispatch(setAlert({ heading: 'Please wait...', type: ALERT_INFO }))
    }

    if (authenticated) {
      dispatch(clearAlert())
    }
  }, [authenticated, authLoading, dispatch, navigate])

  if (authenticated) {
    return (
      <PermissionGuard
        requiresApproval={requiresApproval}
        requiredPermissions={requiredPermissions}
        notAllowedComponent={<Navigate to="/home" />}
      >
        <PrivateTemplate title={title}>
          {children}
          <IdleTimer />
        </PrivateTemplate>
      </PermissionGuard>
    )
  }

  return null
}

export default PrivateRoute
