import React, { useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import closeIcon from 'uswds/dist/img/close.svg'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt, faUserCircle } from '@fortawesome/free-solid-svg-icons'

import NavItem from '../NavItem/NavItem'

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
  const [isMenuVisible, setIsMenuVisible] = useState(false)
  const user = useSelector((state) => state.auth.user)
  const authenticated = useSelector((state) => state.auth.authenticated)

  const menuRef = useRef()

  const handleTabKey = (e) => {
    if (menuRef.current.classList.contains('is-visible')) {
      e.preventDefault()
      const focusableMenuElements = [
        ...menuRef.current.querySelectorAll('button'),
        ...menuRef.current.querySelectorAll('a'),
      ]

      console.log(focusableMenuElements)

      const firstElement = focusableMenuElements[0]
      const lastIndex = focusableMenuElements.length - 1
      const lastElement = focusableMenuElements[lastIndex]

      let tabIndex
      console.log(document.activeElement)

      if (focusableMenuElements.includes(document.activeElement)) {
        tabIndex =
          focusableMenuElements.findIndex(
            (e) => document.activeElement === e
          ) || 0
        console.log('starting with', tabIndex, focusableMenuElements[tabIndex])
        if (!e.shiftKey && tabIndex >= lastIndex) {
          console.log('return to first element')
          tabIndex = 0
        } else if (e.shiftKey && tabIndex === 0) {
          console.log('return to last element')
          tabIndex = lastIndex
        } else if (e.shiftKey) {
          console.log('move back one')
          tabIndex -= 1
        } else {
          console.log('move forward one')
          tabIndex += 1
        }
      } else {
        console.log('refocus to close')
        tabIndex = 0
      }
      console.log('ending on index', tabIndex, focusableMenuElements[tabIndex])
      focusableMenuElements[tabIndex].focus()
    }

    return null
  }

  const keyListenersMap = new Map([[9, handleTabKey]])

  useEffect(() => {
    function keyListener(e) {
      const listener = keyListenersMap.get(e.keyCode)
      return listener && listener(e)
    }
    document.addEventListener('keydown', keyListener)

    return () => document.removeEventListener('keydown', keyListener)
  }, [])

  const isOFASystemAdmin = () => {
    return user?.roles?.some((role) => role.name === 'OFA System Admin')
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
                  {isOFASystemAdmin() && (
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
              </ul>
            </div>
          </div>
        </nav>
      </header>
    </>
  )
}

export default HeaderComp
