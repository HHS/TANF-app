import React from 'react'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'
import { useSelector } from 'react-redux'

function Dashboard() {
  const user = useSelector((state) => state.auth.user.email)
  const handleClick = (event) => {
    event.preventDefault()
    window.location = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }
  return (
    <GridContainer className="welcome">
      <Grid row>
        <Grid col={user ? 8 : 6} className="left">
          <h1>
            Welcome{user ? <em> {user}</em> : ''}!
            <span role="img" aria-label="wave" aria-hidden="true">
              {' '}
              🎉
            </span>
          </h1>
        </Grid>
        <Grid col={user ? 4 : 6} className="right">
          <Button type="button" size="big" onClick={handleClick}>
            Sign Out
          </Button>
        </Grid>
      </Grid>
    </GridContainer>
  )
}

export default Dashboard
