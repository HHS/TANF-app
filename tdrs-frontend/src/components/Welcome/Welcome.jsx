import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'
import { setUser } from '../../actions/auth'

import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'

import './Welcome.scss'

function Welcome() {
  const dispatch = useDispatch()
  const user = useSelector((state) => state.router.location.query.user)
  useEffect(() => {
    if (user) {
      dispatch(setUser(user))
    }
  }, [user, dispatch])
  const handleClick = (event) => {
    event.preventDefault()
    window.location = 'http://localhost:8000/login/oidc'
  }
  return (
    <>
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
    </>
  )
}

export default Welcome
