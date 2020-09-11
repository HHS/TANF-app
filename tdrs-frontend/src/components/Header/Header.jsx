import React, { useState } from 'react'
import { useSelector } from 'react-redux'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt, faUserCircle } from '@fortawesome/free-solid-svg-icons'

import './Header.scss'

import {
  NavMenuButton,
  Header,
  Title,
  ExtendedNav,
  Button,
} from '@trussworks/react-uswds'

/**
 * This component is rendered on every page and contains the navigation bar.
 * When a user is authenticated, it will also display their email and will
 * display a sign out button and when clicked, the user is redirected to the
 * backend's logout endpoint, initiating the logout process.
 *
 * @param {object} pathname - the window's path
 * @param {object} authenticated - whether the user is authenticated or not
 * @param {object} user - the current user's information
 */
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
      className={`usa-nav__link ${
        pathname === '/edit-profile' ? 'usa-current' : ''
      }`}
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
      <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
      Sign Out
    </Button>
  )

  const accountBtn = ({ email }) => (
    <Button type="button" small unstyled>
      <FontAwesomeIcon className="margin-right-1" icon={faUserCircle} />
      {email}
    </Button>
  )

  return (
    <>
      <a className="usa-skipnav" href="#main-content" tabIndex={1}>
        Skip to main content
      </a>
      <div className={`usa-overlay ${mobileNavOpen ? 'is-visible' : ''}`} />
      <section>
        <Header extended>
          <div className="usa-navbar">
            <Title className="page-title">
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
            secondaryItems={authenticated ? [accountBtn(user), signOutBtn] : []}
            onToggleMobileNav={toggleMobileNav}
            mobileExpanded={mobileNavOpen}
          />
        </Header>
      </section>
    </>
  )
}

export default HeaderComp
