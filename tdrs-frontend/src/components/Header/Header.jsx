import React, { useEffect, useMemo, useRef } from 'react'
import { useSelector } from 'react-redux'
import closeIcon from 'uswds/dist/img/close.svg'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt, faUserCircle } from '@fortawesome/free-solid-svg-icons'
import {
  accountStatusIsApproved,
  accountIsInReview,
  accountCanViewAdmin,
  accountCanViewKibana,
} from '../../selectors/auth'

import NavItem from '../NavItem/NavItem'
import PermissionGuard from '../PermissionGuard'

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
function Header() {
  const pathname = useSelector((state) => state.router.location.pathname)
  const user = useSelector((state) => state.auth.user)
  const authenticated = useSelector((state) => state.auth.authenticated)
  const userAccessRequestPending = useSelector(accountIsInReview)
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)
  const userIsAdmin = useSelector(accountCanViewAdmin)
  const userIsSysAdmin = useSelector(accountCanViewKibana)

  const menuRef = useRef()

  const keyListenersMap = useMemo(() => {
    let tabIndex = 0
    /* istanbul ignore next  */
    const handleTabKey = (e) => {
      /* istanbul ignore if */
      if (menuRef.current.classList.contains('is-visible')) {
        e.preventDefault()
        const focusableMenuElements = [
          ...menuRef.current.querySelectorAll('button'),
          ...menuRef.current.querySelectorAll('a'),
        ]

        const lastIndex = focusableMenuElements.length - 1

        if (focusableMenuElements.includes(document.activeElement)) {
          if (!e.shiftKey && tabIndex >= lastIndex) {
            tabIndex = 0
          } else if (e.shiftKey && tabIndex === 0) {
            tabIndex = lastIndex
          } else if (e.shiftKey) {
            tabIndex -= 1
          } else {
            tabIndex += 1
          }
        } else {
          tabIndex = 0
        }

        focusableMenuElements[tabIndex].focus()
      }

      return false
    }

    return new Map([[9, handleTabKey]])
  }, [menuRef])

  /* istanbul ignore next  */
  useEffect(() => {
    function keyListener(e) {
      const listener = keyListenersMap.get(e.keyCode)
      return listener && listener(e)
    }

    document.addEventListener('keydown', keyListener)

    return () => document.removeEventListener('keydown', keyListener)
  }, [keyListenersMap])

  return (
    <>
      <div className="usa-overlay" />
      <header className="usa-header usa-header--extended">
        <div className="grid-container-widescreen usa-nav__wide desktop:padding-left-4 desktop:border-bottom-0 mobile:border-bottom-1px mobile:padding-left-0  mobile:padding-right-0">
          <div className="usa-logo" id="extended-logo">
            <em className="usa-logo__text">
              <a href="/" title="Home" aria-label="Home">
                TANF Data Portal
              </a>
            </em>
          </div>
          {authenticated && (
            <button type="button" className="usa-menu-btn">
              Menu
            </button>
          )}
        </div>
        <nav
          ref={menuRef}
          role="navigation"
          aria-label="Primary navigation"
          className="usa-nav"
        >
          <div className="grid-container-widescreen">
            <button type="button" className="usa-nav__close">
              <img src={closeIcon} alt="close" />
            </button>
            <ul className="usa-nav__primary usa-accordion">
              {authenticated && (
                <>
                  <NavItem pathname={pathname} tabTitle="Home" href="/home" />
                  <PermissionGuard
                    requiresApproval
                    requiredPermissions={['view_datafile', 'add_datafile']}
                  >
                    <NavItem
                      pathname={pathname}
                      tabTitle="Data Files"
                      href="/data-files"
                    />
                  </PermissionGuard>
                  {(userAccessRequestPending || userAccessRequestApproved) && (
                    <NavItem
                      pathname={pathname}
                      tabTitle="Profile"
                      href="/profile"
                    />
                  )}
                  {userIsAdmin && (
                    <NavItem
                      pathname={pathname}
                      tabTitle="Admin"
                      href={`${process.env.REACT_APP_BACKEND_HOST}/admin/`}
                    />
                  )}
                  {userIsSysAdmin && (
                    <NavItem
                      pathname={pathname}
                      tabTitle="Kibana"
                      href={`${process.env.REACT_APP_BACKEND_HOST}/kibana/`}
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
                {authenticated && (
                  <li className="usa-nav__secondary-item">
                    <a
                      className="sign-out-link"
                      href={`${process.env.REACT_APP_BACKEND_URL}/logout/oidc`}
                    >
                      <FontAwesomeIcon
                        className="margin-right-1"
                        icon={faSignOutAlt}
                      />
                      Sign Out
                    </a>
                  </li>
                )}
              </ul>
            </div>
          </div>
        </nav>
      </header>
    </>
  )
}

export default Header
