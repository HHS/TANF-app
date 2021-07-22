import React from 'react'
import { useSelector } from 'react-redux'

import closeIcon from 'uswds/dist/img/close.svg'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt, faUserCircle } from '@fortawesome/free-solid-svg-icons'
import NavItem from '../NavItem/NavItem'

const SignoutLink = ({ user }) => (
  <a
    className="sign-out-link"
    href={
      user && user.email
        ? `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
        : `${process.env.REACT_APP_BACKEND_URL}/login/oidc`
    }
  >
    <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
    {user && user.email ? 'Sign Out' : 'Sign In'}
  </a>
)
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
  const user = useSelector((state) => state.auth.user)
  const authenticated = useSelector((state) => state.auth.authenticated)

  const isSystemAdmin = () => {
    return user?.roles?.some((role) => role.name === 'System Admin')
  }

  return (
    <>
      <div className="usa-overlay" />
      <header className="usa-header usa-header--extended">
        <div className="usa-navbar">
          <div className="usa-logo" id="extended-logo">
            <em className="usa-logo__text">
              <a href="/" title="Home" aria-label="Home">
                TANF Data Portal
              </a>
            </em>
          </div>
          <button type="button" className="usa-menu-btn">
            Menu
          </button>
        </div>
        <nav aria-label="Primary navigation" className="usa-nav">
          <div className="usa-nav__inner">
            <button type="button" className="usa-nav__close">
              <img src={closeIcon} alt="close" />
            </button>
            <ul className="usa-nav__primary usa-accordion">
              {authenticated && (
                <>
                  <NavItem
                    pathname={pathname}
                    tabTitle="Welcome"
                    href="/welcome"
                  />
                  <NavItem
                    pathname={pathname}
                    tabTitle="Data Files"
                    href="/data-files"
                  />
                  <NavItem
                    pathname={pathname}
                    tabTitle="Profile"
                    href="/edit-profile"
                  />
                  {isSystemAdmin() && (
                    <NavItem
                      pathname={pathname}
                      tabTitle="Admin"
                      href={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
                    />
                  )}
                </>
              )}
            </ul>
            <div className="usa-nav__secondary">
              <ul className="usa-nav__secondary-links">
                <li
                  className={`${
                    user && user.email ? 'display-block' : 'display-none'
                  } usa-nav__secondary-item`}
                >
                  {user && user.email && (
                    <a href="/">
                      <FontAwesomeIcon
                        className="margin-right-1"
                        icon={faUserCircle}
                      />
                      {user && user.email}
                    </a>
                  )}
                </li>
                <li className="usa-nav__secondary-item">
                  {process.env.REACT_APP_USE_MIRAGE ? (
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        // localStorage converts all values to strings, so to get a falsy value
                        // we pass in a blank string
                        window.localStorage.setItem('loggedIn', '')
                        window.location.reload()
                      }}
                    >
                      <SignoutLink user={user} />
                    </button>
                  ) : (
                    <SignoutLink user={user} />
                  )}
                </li>
              </ul>
            </div>
          </div>
        </nav>
      </header>
    </>
  )
}

export default HeaderComp
