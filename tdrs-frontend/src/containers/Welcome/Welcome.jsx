import React from 'react'
import { useDispatch } from 'react-redux'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'
import { login } from '../../actions/auth'

import '@trussworks/react-uswds/lib/uswds.css'
import '@trussworks/react-uswds/lib/index.css'

import './Welcome.scss'

function Welcome() {
  const dispatch = useDispatch()
  const handleClick = (event) => {
    event.preventDefault()
    dispatch(login())
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
