import React from 'react'
import { Footer, Logo, SocialLinks, Grid } from '@trussworks/react-uswds'

import ACFLogo from '../../assets/placeholder.png'

import './Footer.scss'

/**
 * This component is rendered on every page and contains
 * the department logo and social links.
 */
function renderFooter() {
  return (
    <Footer
      size="big"
      primary={null}
      secondary={
        <Grid row gap>
          <Logo
            size="big"
            image={
              <img
                className="usa-footer__logo-img"
                alt="Administration for Children and Families Logo"
                src={ACFLogo}
              />
            }
          />
        </Grid>
      }
    />
  )
}

export default renderFooter
