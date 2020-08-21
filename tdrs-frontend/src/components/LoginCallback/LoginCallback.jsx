import React, { useEffect } from 'react'
import { Redirect } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Notify'

function LoginCallback() {
  const authLoading = useSelector((state) => state.auth.loading)
  const authenticated = useSelector((state) => state.auth.authenticated)
  const dispatch = useDispatch()

  useEffect(() => {
    if (authLoading) {
      dispatch(setAlert({ heading: 'Signing In...', type: ALERT_INFO }))
    }

    if (authenticated) {
      dispatch(clearAlert())
    }
  }, [authenticated, authLoading, dispatch])

  if (!authenticated && !authLoading) {
    return <Redirect to="/" />
  }

  return authenticated ? <Redirect to="/dashboard" /> : null
}

export default LoginCallback
