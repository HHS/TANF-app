import React from 'react'
import { GridContainer, Button, Grid } from '@trussworks/react-uswds'
import { useSelector } from 'react-redux'
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
  const user = useSelector((state) => state.auth.user.email)
  const handleClick = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
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
            <a className="usa-button" href="javascript:void(0)">
              Sign in with LOGIN.GOV
            </a>
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

      {/* <section className="usa-graphic-list usa-section usa-section--dark">
        <GridContainer>
          <Grid row gap className="usa-graphic-list__row">
            <Grid tablet={{ col: true }} className="usa-media-block">
              <img
                className="usa-media-block__img"
                src={circleImg}
                alt="Alt text"
              />
              <div className="usa-media-block__body">
                <h2 className="usa-graphic-list__heading">
                  Graphic headings can vary.
                </h2>
                <p>
                  Graphic headings can be used a few different ways, depending
                  on what your landing page is for. Highlight your values,
                  specific program areas, or results.
                </p>
              </div>
            </Grid>
            <Grid tablet={{ col: true }} className="usa-media-block">
              <img
                className="usa-media-block__img"
                src={circleImg}
                alt="Alt text"
              />
              <div className="usa-media-block__body">
                <h2 className="usa-graphic-list__heading">
                  Stick to 6 or fewer words.
                </h2>
                <p>
                  Keep body text to about 30 words. They can be shorter, but
                  try to be somewhat balanced across all four. It creates a
                  clean appearance with good spacing.
                </p>
              </div>
            </Grid>
          </Grid>
          <Grid row gap className="usa-graphic-list__row">
            <Grid tablet={{ col: true }} className="usa-media-block">
              <img
                className="usa-media-block__img"
                src={circleImg}
                alt="Alt text"
              />
              <div className="usa-media-block__body">
                <h2 className="usa-graphic-list__heading">
                  Never highlight anything without a goal.
                </h2>
                <p>
                  For anything you want to highlight here, understand what
                  your users know now, and what activity or impression you
                  want from them after they see it.
                </p>
              </div>
            </Grid>
            <Grid tablet={{ col: true }} className="usa-media-block">
              <img
                className="usa-media-block__img"
                src={circleImg}
                alt="Alt text"
              />
              <div className="usa-media-block__body">
                <h2 className="usa-graphic-list__heading">
                  Could also have 2 or 6.
                </h2>
                <p>
                  In addition to your goal, find out your users’ goals. What
                  do they want to know or do that supports your mission? Use
                  these headings to show these.
                </p>
              </div>
            </Grid>
          </Grid>
        </GridContainer>
      </section>

      <section id="test-section-id" className="usa-section">
        <GridContainer>
          <h2 className="font-heading-xl margin-y-0">Section heading</h2>
          <p className="usa-intro">
            Everything up to this point should help people understand your
            agency or project: who you are, your goal or mission, and how you
            approach it. Use this section to encourage them to act. Describe
            why they should get in touch here, and use an active verb on the
            button below. “Get in touch,” “Learn more,” and so on.
          </p>
          <a href="#" className="usa-button usa-button--big">
            Call to action
          </a>
        </GridContainer>
      </section> */}
    </main>
  )
}

export default Dashboard
