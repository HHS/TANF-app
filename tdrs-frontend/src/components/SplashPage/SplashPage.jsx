import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'
import {
  GridContainer,
  Button,
  Grid,
  Link,
  CardGroup,
  Card,
} from '@trussworks/react-uswds'

import './SplashPage.scss'
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
function SplashPage() {
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
    <div>
      <section className="usa-hero" aria-label="Introduction">
        <GridContainer>
          <Grid>
            <div className="usa-hero__callout">
              <h1 className="usa-hero__heading">
                <span className="usa-hero__heading--alt margin-bottom-6">
                  Sign into TANF Data Portal
                </span>
              </h1>
              <p className="text-black margin-bottom-6">
                Our vision is to build a new, secure, web based data reporting
                system to improve the federal reporting experience for TANF
                grantees and federal staff. The new system will allow grantees
                to easily submit accurate data and be confident that they have
                fulfilled their reporting requirements.
              </p>
              <Button
                className="sign-in-button"
                type="button"
                size="big"
                onClick={handleClick}
              >
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
            tablet={{ col: 4 }}
            mobileLg={{ col: 12 }}
          >
            <h2 className="resources-header font-heading-2xl margin-top-0 tablet:margin-bottom-0">
              Featured TANF Resources
            </h2>
            <div className="font-heading-3xs resource-info__secondary">
              <p>Questions about TANF data?</p>
              <p>
                Email:{' '}
                <Link href="mailto: tanfdata@acf.hhs.gov">
                  tanfdata@acf.hhs.gov
                </Link>
              </p>
            </div>
          </Grid>
          <Grid tablet={{ col: 8 }} mobileLg={{ col: 12 }} row gap>
            <CardGroup className="grid-col-12">
              <Card className="resource-card tablet:grid-col-4 mobile-lg:grid-col-12">
                Resource 1
              </Card>
              <Card className="resource-card tablet:grid-col-4 mobile-lg:grid-col-12">
                Resource 2
              </Card>
              <Card className="resource-card tablet:grid-col-4 mobile-lg:grid-col-12">
                Resource 3
              </Card>
            </CardGroup>
          </Grid>
        </Grid>
      </GridContainer>
    </div>
  )
}

export default SplashPage
