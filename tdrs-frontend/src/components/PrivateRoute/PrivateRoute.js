import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import { Route, withRouter } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Alert'
import IdleTimer from '../IdleTimer/IdleTimer'

/**
 *
 * @param {string} path - the path to route to
 * @param {component(s)} children - One or more React components to be rendered
 * if the user is authenticated
 * @param {object} history - the window's history object,
 * which is automatically passed via withRouter
 */
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

  return authenticated ? (
    <Route path={path}>
      <IdleTimer />
      {children}
    </Route>
  ) : null
}

PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
  }).isRequired,
  path: PropTypes.string.isRequired,
}

export default withRouter(PrivateRoute)
