import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import { Route, withRouter } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Notify'

function PrivateRoute({ children, history, path }) {
  const authenticated = useSelector((state) => state.auth.authenticated)
  const authLoading = useSelector((state) => state.auth.loading)
  const dispatch = useDispatch()

  useEffect(() => {
    if (!authenticated && !authLoading) {
      dispatch(setAlert({ heading: 'Please sign in first', type: ALERT_INFO }))
      history.push('/')
    }

    if (authLoading) {
      dispatch(setAlert({ heading: 'Please wait...', type: ALERT_INFO }))
    }

    if (authenticated) {
      dispatch(clearAlert())
    }
  }, [authenticated, authLoading, dispatch, history])

  return authenticated ? <Route path={path}>{children}</Route> : null
}

PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  path: PropTypes.string.isRequired,
}

export default withRouter(PrivateRoute)
