import React, { useEffect } from 'react'
import { Redirect } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Notify'

/**
 * This component renders momentarily after the user logs in.
 * Upon login, the API redirects here via `/login`
 * If the final authentication check is still processing,
 * the component dispatches an action to notify the user
 * that the page is loading. When the page is done loading,
 * that alert is cleared.
 *
 * If the user is not authenticated, and if there isn't even
 * an authentication check in progress, the user is redirected
 * to the home page.
 *
 * If the user is logged in, when landing on this component
 * the user is redirected to his/her Dashboard.
 *
 * @param {boolean} authLoading
 *  - whether there is an authentication check in progress
 * @param {boolean} authenticated - whether user is authenticated
 */
function LoginCallback() {
  const authLoading = useSelector((state) => state.auth.loading)
  const authenticated = useSelector((state) => state.auth.authenticated)
  const dispatch = useDispatch()

  useEffect(() => {
    if (authLoading) {
      dispatch(setAlert({ heading: 'Please wait...', type: ALERT_INFO }))
    } else {
      dispatch(clearAlert())
    }
  }, [authenticated, authLoading, dispatch])

  if (!authenticated && !authLoading) {
    return <Redirect to="/" />
  }

  return authenticated ? <Redirect to="/dashboard" /> : null
}

export default LoginCallback
