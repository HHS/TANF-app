import React from 'react'
import { GridContainer, Grid, Logo, SocialLinks } from '@trussworks/react-uswds'

import ACFLogo from '../../assets/ACFLogo.svg'

import './Footer.scss'

function Footer() {
  const socialLinks = [
    <a
      key="facebook"
      className="usa-social-link usa-social-link--facebook"
      href="/"
    >
      <span>Facebook</span>
    </a>,
    <a
      key="youtube"
      className="usa-social-link usa-social-link--youtube"
      href="/"
    >
      <span>YouTube</span>
    </a>,
    <a key="rss" className="usa-social-link usa-social-link--rss" href="/">
      <span>RSS</span>
    </a>,
  ]

  return (
    <section className="bg-primary-lighter footer-container">
      <GridContainer>
        <Grid row>
          <Logo
            big
            image={
              <img
                className="usa-footer__logo-img"
                src={ACFLogo}
                alt="Administration for Children and Families Logo"
              />
            }
          />
          <Grid
            className="padding-right-0 usa-footer__contact-links"
            mobileLg={{ col: 6 }}
          >
            <SocialLinks links={socialLinks} />
          </Grid>
        </Grid>
      </GridContainer>
    </section>
  )
}

export default Footer
