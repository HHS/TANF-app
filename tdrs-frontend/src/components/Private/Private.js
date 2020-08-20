import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import { Route } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Notify'

export default function Private({ children, history, path }) {
  const authenticated = useSelector((state) => state.auth.authenticated)
  const authLoading = useSelector((state) => state.auth.loading)
  const dispatch = useDispatch()

  useEffect(() => {
    if (!authenticated && authLoading) {
      dispatch(setAlert({ heading: 'Signing In...', type: ALERT_INFO }))
    }

    if (!authenticated && !authLoading) {
      dispatch(setAlert({ heading: 'Please login first', type: ALERT_INFO }))
      history.push('/')
    }

    if (authenticated) {
      dispatch(clearAlert())
    }
  }, [authenticated, authLoading, dispatch, history])

  return <Route path={path}>{children}</Route>
}

Private.propTypes = {
  children: PropTypes.node.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  path: PropTypes.string.isRequired,
}
