import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'
import circleImg from '../../matt-wang-eNwx-kYd6fM-unsplash.jpg'

/**
 * This component renders for a user who just logged in.
 * It renders a sign-out button and when clicked,
 * the user is redirected to the backend's logout endpoint,
 * initiating the logout process.
 *
 * @param {object} email - a user's email address
 */
function Dashboard() {
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
    <main id="main-content">
      <section className="usa-hero" aria-label="Introduction">
        <GridContainer>
          <div className="usa-hero__callout">
            <h1 className="usa-hero__heading">
              <span className="usa-hero__heading--alt">Sign into TANF Data Portal</span>
            </h1>
            <p>
              Our vision is to build a new, secure, web based data reporting system to improve 
              the federal reporting experience for TANF grantees and federal staff. 
              The new system will allow grantees to easily submit accurate data and be confident 
              that they have fulfilled their reporting requirements.
            </p>
            <Button type="button" size="big" onClick={handleClick}>
              Sign in with Login.gov
            </Button>
          </div>
        </GridContainer>
      </section>

      <section className="grid-container usa-section">
        <Grid row gap>
          <Grid tablet={{ col: 4 }}>
            <h2 className="font-heading-xl margin-top-0 tablet:margin-bottom-0">
              Featured TANF Resources
            </h2>
            <p>
              Questions about TANF data?
            </p>
            <p>
              Email: tanfdata@acf.hhs.gov
            </p>
          </Grid>
          <Grid tablet={{ col: 8 }}>
            <img
              className="usa-media-block__img"
              src={circleImg}
              style={{height: '120px' }}
              alt="Alt text"
            />
            <img
              className="usa-media-block__img"
              src={circleImg}
              style={{height: '120px' }}
              alt="Alt text"
            />
            <img
              className="usa-media-block__img"
              src={circleImg}
              style={{height: '120px' }}
              alt="Alt text"
            />
          </Grid>
        </Grid>
      </section>
    </main>
  )
}

export default Dashboard
