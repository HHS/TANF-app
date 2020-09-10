import React from 'react'
import { Footer, Logo, SocialLinks } from '@trussworks/react-uswds'

import ACFLogo from '../../assets/placeholder.png'

/**
 * This component is rendered on every page and contains
 * the department logo and social links.
 */
function renderFooter() {
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
    <Footer
      size="big"
      primary={null}
      secondary={
        <div className="grid-row grid-gap">
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
          <div className="usa-footer__contact-links mobile-lg:grid-col-6">
            <SocialLinks links={socialLinks} />
          </div>
        </div>
      }
    />
  )
}

export default renderFooter
