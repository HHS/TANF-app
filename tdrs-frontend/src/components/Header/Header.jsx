import React from 'react'
import { useSelector } from 'react-redux'

import closeIcon from 'uswds/dist/img/close.svg'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt, faUserCircle } from '@fortawesome/free-solid-svg-icons'

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
              <li className="usa-nav__primary-item">
                <a
                  href="/"
                  key="welcome"
                  className={`usa-nav__link ${
                    pathname === '/edit-profile' ? 'usa-current' : ''
                  }`}
                >
                  <span>Welcome</span>
                </a>
              </li>
            </ul>
            {user && (
              <div className="usa-nav__secondary">
                <ul className="usa-nav__secondary-links">
                  <li className="usa-nav__secondary-item">
                    <a href="/">
                      <FontAwesomeIcon
                        className="margin-right-1"
                        icon={faUserCircle}
                      />
                      {user.email}
                    </a>
                  </li>
                  <li className="usa-nav__secondary-item">
                    <a
                      href={`${process.env.REACT_APP_BACKEND_URL}/logout/oidc`}
                    >
                      <FontAwesomeIcon
                        className="margin-right-1"
                        icon={faSignOutAlt}
                      />
                      Sign Out
                    </a>
                  </li>
                </ul>
              </div>
            )}
          </div>
        </nav>
      </header>
    </>
  )
}

export default HeaderComp
