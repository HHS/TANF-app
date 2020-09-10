import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'

import './Welcome.scss'

/**
 * This component renders on all pages of the TANF Data Portal.
 * It renders a hero element with a login button and when clicked
 * the user is redirected to the backend's login endpoint,
 * initiating the sign in process.
 *
 * @param {boolean} authenticated - has user been authenticated
 * @param {boolean} authLoading - set to true when checking if user
 * is authenticated.
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
    <div class="wrapper">
      <section className="usa-hero" aria-label="Introduction">
        <GridContainer>
          <Grid>
            <div className="usa-hero__callout">
              <h1 className="usa-hero__heading">
                <span className="usa-hero__heading--alt">
                  Sign into TANF Data Portal
                </span>
              </h1>
              <p>
                Our vision is to build a new, secure, web based data reporting
                system to improve the federal reporting experience for TANF
                grantees and federal staff. The new system will allow grantees
                to easily submit accurate data and be confident that they have
                fulfilled their reporting requirements.
              </p>
              <Button type="button" size="big" onClick={handleClick}>
                Sign in with Login.gov
                <span className="visually-hidden">Opens in a new website</span>
              </Button>
            </div>
          </Grid>
        </GridContainer>
      </section>

      <GridContainer className="usa-section">
        <Grid row gap>
          <Grid
            className="resource-info__primary"
            tablet={{ col: 6 }}
            mobileLg={{ col: 12 }}
          >
            <h2 className="font-heading-xl margin-top-0 tablet:margin-bottom-0">
              Featured TANF Resources
            </h2>
            <div className="font-heading-3xs resource-info__secondary">
              <p>Questions about TANF data?</p>
              <p>Email: tanfdata@acf.hhs.gov</p>
            </div>
          </Grid>
          <Grid
            tablet={{ col: true }}
            className="tablet:margin-bottom-0 mobile-lg:margin-bottom-2"
          >
            <div className="resource-card">Resource 1</div>
          </Grid>
          <Grid
            tablet={{ col: true }}
            className="tablet:margin-bottom-0 mobile-lg:margin-bottom-2"
          >
            <div className="resource-card">Resource 2</div>
          </Grid>
          <Grid
            tablet={{ col: true }}
            className="tablet:margin-bottom-0 mobile-lg:margin-bottom-2"
          >
            <div className="resource-card">Resource 3</div>
          </Grid>
        </Grid>
      </GridContainer>
    </div>
  )
}

export default Welcome
