import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Alert'
import PrivateTemplate from '../PrivateTemplate'
import IdleTimer from '../IdleTimer/IdleTimer'

/**
 * @param {React.ReactNode} children - One or more React components to be
 * rendered if the user is authenticated
 * @param {string} title Page title passed in to PrivateTemplate
 * which is automatically passed via withRouter
 */
function PrivateRoute({ children, title }) {
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

  return authenticated ? (
    <PrivateTemplate title={title}>
      {children}
      <IdleTimer />
    </PrivateTemplate>
  ) : null
}

export default PrivateRoute
