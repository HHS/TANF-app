import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'

import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'

import './Welcome.scss'

/**
 * This component renders at the '/' route
 * when a user is not logged in.
 *
 * If a user is logged in, it redirects them to '/dashboard'
 *
 * If user not logged in, and clicks log in,
 * it redirects user to API's login route
 * which forwards them to login.gov
 *
 * @param {boolean} authLoading
 *  - whether there is an authentication check in progress
 * @param {boolean} authenticated - whether user is authenticated
 */
function Welcome() {
  const authenticated = useSelector((state) => state.auth.authenticated)
  const authLoading = useSelector((state) => state.auth.loading)

  const handleClick = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login/oidc`
  }

  if (authenticated) {
    return <Redirect to="/dashboard" />
  }

  if (authLoading) {
    return null
  }

  return (
    <GridContainer className="welcome">
      <Grid row>
        <Grid col={6} className="left">
          <h1>
            Welcome to TDRS!
            <span role="img" aria-label="wave" aria-hidden="true">
              {' '}
              👋
            </span>
          </h1>
        </Grid>
        <Grid col={6} className="right">
          <Button type="button" size="big" onClick={handleClick}>
            Sign in with Login.gov
          </Button>
        </Grid>
      </Grid>
    </GridContainer>
  )
}

export default Welcome
