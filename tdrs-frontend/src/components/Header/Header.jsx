import React, { useState } from 'react'
import { useSelector } from 'react-redux'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'

import {
  NavMenuButton,
  Header,
  Title,
  ExtendedNav,
  Button,
  Grid,
} from '@trussworks/react-uswds'

function HeaderComp() {
  const pathname = useSelector((state) => state.router.location.pathname)
  const authenticated = useSelector((state) => state.auth.authenticated)
  const user = useSelector((state) => state.auth.user)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const toggleMobileNav = () => {
    setMobileNavOpen((prevOpen) => !prevOpen)
  }

  const navigationBar = [
    <a
      href="/"
      key="welcome"
      className={`usa-nav__link ${pathname === '/' ? 'usa-current' : ''}`}
    >
      <span>Welcome</span>
    </a>,
  ]

  const handleClick = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  const signOutBtn = (
    <Button
      className="sign-out"
      type="button"
      small
      unstyled
      onClick={handleClick}
    >
      <Grid offset={4}>
        <FontAwesomeIcon icon={faSignOutAlt} />
      </Grid>
      <Grid>Sign Out</Grid>
    </Button>
  )

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
          secondaryItems={authenticated ? [user.email, signOutBtn] : []}
          onToggleMobileNav={toggleMobileNav}
          mobileExpanded={mobileNavOpen}
        />
      </Header>
    </>
  )
}

export default HeaderComp
