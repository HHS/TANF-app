import React, { useState } from 'react'

import {
  NavMenuButton,
  Header,
  Title,
  ExtendedNav,
} from '@trussworks/react-uswds'

function HeaderComp() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const toggleMobileNav = () => {
    setMobileNavOpen((prevOpen) => !prevOpen)
  }

  const navigationBar = [
    <a href="/" key="welcome" className="usa-nav__link">
      <span>Welcome</span>
    </a>,
  ]

  return (
    <>
      <a className="usa-skipnav" href="#main-content">
        Skip to main content
      </a>
      <div className={`usa-overlay ${mobileNavOpen ? 'is-visible' : ''}`} />
      <Header extended>
        <div className="usa-navbar">
          <Title>
            <a href="/" title="Home" aria-label="Home">
              TANF Data Portal
            </a>
          </Title>
          <NavMenuButton
            label="Menu"
            onClick={toggleMobileNav}
            className="usa-menu-btn"
          />
        </div>
        <ExtendedNav
          primaryItems={navigationBar}
          secondaryItems={[]}
          onToggleMobileNav={toggleMobileNav}
          mobileExpanded={mobileNavOpen}
        />
      </Header>
    </>
  )
}

export default HeaderComp
