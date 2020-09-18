import React, { useState } from 'react'
import { useSelector } from 'react-redux'

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
  const authenticated = useSelector((state) => state.auth.authenticated)
  const user = useSelector((state) => state.auth.user)
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const toggleMobileNav = () => {
    setMobileNavOpen((prevOpen) => !prevOpen)
  }

  const primaryNav = [
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

  const renderSecondaryNav = ({ email }) => [
    <a className="account-link" href="/">
      <FontAwesomeIcon className="margin-right-1" icon={faUserCircle} />
      {email}
    </a>,
    <a
      className="sign-out-link"
      href={`${process.env.REACT_APP_BACKEND_URL}/logout/oidc`}
    >
      <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
      Sign Out
    </a>,
  ]

  return (
    <>
      <section className="usa-banner" aria-label="Official government website">
        <div className="usa-accordion">
          <header className="usa-banner__header">
            <div className="usa-banner__inner">
              <div className="grid-col-auto">
                <img
                  className="usa-banner__header-flag"
                  src="/assets/img/us_flag_small.png"
                  alt="U.S. flag"
                />
              </div>
              <div className="grid-col-fill tablet:grid-col-auto">
                <p className="usa-banner__header-text">
                  An official website of the United States government
                </p>
                <p className="usa-banner__header-action" aria-hidden="true">
                  Here’s how you know
                </p>
              </div>
              <button
                type="button"
                className="usa-accordion__button usa-banner__button"
                aria-expanded="false"
                aria-controls="gov-banner"
              >
                <span className="usa-banner__button-text">
                  Here’s how you know
                </span>
              </button>
            </div>
          </header>
          <div
            className="usa-banner__content usa-accordion__content"
            id="gov-banner"
          >
            <div className="grid-row grid-gap-lg">
              <div className="usa-banner__guidance tablet:grid-col-6">
                <img
                  className="usa-banner__icon usa-media-block__img"
                  src="/assets/img/icon-dot-gov.svg"
                  alt="Dot gov"
                />
                <div className="usa-media-block__body">
                  <p>
                    <strong>Official websites use .gov</strong>
                    <br />A <strong>.gov</strong> website belongs to an official
                    government organization in the United States.
                  </p>
                </div>
              </div>
              <div className="usa-banner__guidance tablet:grid-col-6">
                <img
                  className="usa-banner__icon usa-media-block__img"
                  src="/assets/img/icon-https.svg"
                  alt="Https"
                />
                <div className="usa-media-block__body">
                  <p>
                    <strong>Secure .gov websites use HTTPS</strong>
                    <br />A <strong>lock</strong> (
                    <span className="icon-lock">
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="52"
                        height="64"
                        viewBox="0 0 52 64"
                        className="usa-banner__lock-image"
                        role="img"
                        aria-labelledby="banner-lock-title banner-lock-description"
                      >
                        <title id="banner-lock-title">Lock</title>
                        <desc id="banner-lock-description">
                          A locked padlock
                        </desc>
                        <path
                          fill="#000000"
                          fillRule="evenodd"
                          d="M26 0c10.493 0 19 8.507 19 19v9h3a4 4 0 0 1 4 4v28a4 4 0 0 1-4 4H4a4 4 0 0 1-4-4V32a4 4 0 0 1 4-4h3v-9C7 8.507 15.507 0 26 0zm0 8c-5.979 0-10.843 4.77-10.996 10.712L15 19v9h22v-9c0-6.075-4.925-11-11-11z"
                        />
                      </svg>
                    </span>
                    ) or <strong>https://</strong> means you’ve safely connected
                    to the .gov website. Share sensitive information only on
                    official, secure websites.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="usa-overlay" />
      <header className="usa-header usa-header--extended">
        <div className="usa-navbar">
          <div className="usa-logo" id="extended-logo">
            <em className="usa-logo__text">
              <a href="/" title="Home" aria-label="Home">
                Project title
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
              <img src="/assets/img/close.svg" alt="close" />
            </button>
            <ul className="usa-nav__primary usa-accordion">
              <li className="usa-nav__primary-item">
                <button
                  type="button"
                  className="usa-accordion__button usa-nav__link  usa-current"
                  aria-expanded="false"
                  aria-controls="extended-nav-section-one"
                >
                  <span>Current section</span>
                </button>
                <ul id="extended-nav-section-one" className="usa-nav__submenu">
                  <li className="usa-nav__submenu-item">
                    <a href="/" className="">
                      {' '}
                      Navigation link
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="/" className="">
                      {' '}
                      Navigation link
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="/" className="">
                      {' '}
                      Navigation link
                    </a>
                  </li>
                </ul>
              </li>
              <li className="usa-nav__primary-item">
                <button
                  type="button"
                  className="usa-accordion__button usa-nav__link"
                  aria-expanded="false"
                  aria-controls="extended-nav-section-two"
                >
                  <span>Section</span>
                </button>
                <ul id="extended-nav-section-two" className="usa-nav__submenu">
                  <li className="usa-nav__submenu-item">
                    <a href="/" className="">
                      {' '}
                      Navigation link
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="/" className="">
                      {' '}
                      Navigation link
                    </a>
                  </li>
                  <li className="usa-nav__submenu-item">
                    <a href="/" className="">
                      {' '}
                      Navigation link
                    </a>
                  </li>
                </ul>
              </li>
              <li className="usa-nav__primary-item">
                <a className="usa-nav__link" href="/">
                  <span>Simple link</span>
                </a>
              </li>
            </ul>
            <div className="usa-nav__secondary">
              <ul className="usa-nav__secondary-links">
                <li className="usa-nav__secondary-item">
                  <a href="/">Secondary link</a>
                </li>
                <li className="usa-nav__secondary-item">
                  <a href="/">Another secondary link</a>
                </li>
              </ul>
              <form className="usa-search usa-search--small" role="search">
                <label
                  className="usa-sr-only"
                  htmlFor="extended-search-field-small"
                >
                  Search small
                  <input
                    className="usa-input"
                    id="extended-search-field-small"
                    type="search"
                    name="search"
                  />
                </label>
                <button className="usa-button" type="submit">
                  <span className="usa-sr-only">Search</span>
                </button>
              </form>
            </div>
          </div>
        </nav>
      </header>
    </>
  )
}

export default HeaderComp
