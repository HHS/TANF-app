import React, { useEffect, useRef } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Redirect } from 'react-router-dom'

import { setMockLoginState } from '../../actions/auth'

import loginLogo from '../../assets/login-gov-logo.svg'
import Button from '../Button'

/**
 * SplashPage renders the Welcome page for the TANF Data Portal
 * for an unauthenticated user. If a user logs in, they are automatically
 * redirected to `/edit-profile`.
 */
function SplashPage() {
  const authenticated = useSelector((state) => state.auth.authenticated)
  const authLoading = useSelector((state) => state.auth.loading)
  const isInactive = useSelector((state) => state.auth.inactive)
  const alertRef = useRef(null)
  const dispatch = useDispatch()

  const signInWithLoginDotGov = (event) => {
    /* istanbul ignore if */
    if (
      !window.location.href.match(/https:\/\/.*\.app\.cloud\.gov/) &&
      process.env.REACT_APP_USE_MIRAGE
    ) {
      // This doesn't need to be tested, it will never be reached by jest.
      event.preventDefault()
      dispatch(setMockLoginState())
    } else {
      event.preventDefault()
      window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login/oidc`
    }
  }

  const signInWithAMS = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login/oidc`
  }

  useEffect(() => {
    if (isInactive) {
      setTimeout(() => alertRef?.current?.focus(), 2)
    }
  }, [alertRef, isInactive])

  // Pa11y is not testing out authentication logic, by passing all auth checks
  // during Pa11y tests allows us to just point to a page in the config like
  // we have been doing.
  if (authenticated && !process.env.REACT_APP_PA11Y_TEST) {
    return <Redirect to="/welcome" />
  }

  if (authLoading) {
    return null
  }

  return (
    <>
      <section className="usa-hero" aria-label="Introduction">
        <div className="grid-container">
          {isInactive && (
            <div className="usa-alert usa-alert--slim usa-alert--error margin-bottom-4">
              <div className="usa-alert__body">
                <h3
                  tabIndex="-1"
                  className="usa-alert__heading"
                  ref={alertRef}
                  aria-describedby="errorLabel"
                >
                  Inactive Account
                </h3>
                <p className="usa-alert__text" id="errorLabel">
                  Please email{' '}
                  <a className="usa-link" href="mailto: tanfdata@acf.hhs.gov">
                    tanfdata@acf.hhs.gov
                  </a>{' '}
                  to reactivate your account.
                </p>
              </div>
            </div>
          )}
          <div className="usa-hero__callout">
            <h1 className="usa-hero__heading">
              <span className="usa-hero__heading--alt font-serif-2xl margin-bottom-5">
                Sign into TANF Data Portal
              </span>
            </h1>
            <p className="text-black margin-bottom-5">
              Our vision is to build a new, secure, web based data reporting
              system to improve the federal reporting experience for TANF
              grantees and federal staff. The new system will allow grantees to
              easily submit accurate data and be confident that they have
              fulfilled their reporting requirements.
            </p>
            <Button
              className="width-full sign-in-button"
              type="button"
              onClick={signInWithLoginDotGov}
            >
              <div className="mobile:margin-x-auto mobile-lg:margin-0">
                Sign in with
                <img
                  className="mobile:margin-x-auto mobile:padding-top-1 mobile-lg:margin-0 mobile-lg:padding-top-0 width-15 padding-left-1"
                  src={loginLogo}
                  alt="Login.gov"
                />
                for grantees
              </div>

              <span className="visually-hidden">Opens in a new website</span>
            </Button>
            <Button
              className="width-full sign-in-button margin-top-3"
              type="button"
              onClick={signInWithAMS}
            >
              <div className="mobile:margin-x-auto mobile-lg:margin-0">
                Sign in with ACF AMS for ACF staff
              </div>
              <span className="visually-hidden">Opens in a new website</span>
            </Button>
          </div>
        </div>
      </section>

      <section className="grid-container usa-section">
        <div className="grid-row grid-gap">
          <div className="tablet:grid-col-4">
            <h2 className="resources-header font-heading-2xl margin-top-0 tablet:margin-bottom-0">
              Featured TANF Resources
            </h2>
            <div className="resource-info__secondary">
              <p>Questions about TANF data?</p>
              <p>
                Email:{' '}
                <a className="usa-link" href="mailto: tanfdata@acf.hhs.gov">
                  tanfdata@acf.hhs.gov
                </a>
              </p>
            </div>
          </div>
          <div className="tablet:grid-col-8">
            <ul className="usa-card-group grid-col-12">
              <li className="usa-card tablet:grid-col-4 mobile-lg:grid-col-12 resource-card">
                <div className="usa-card__container">
                  <header className="usa-card__header">
                    <h3 className="usa-card__heading">Resource 1</h3>
                  </header>
                </div>
              </li>
              <li className="usa-card tablet:grid-col-4 mobile-lg:grid-col-12 resource-card">
                <div className="usa-card__container">
                  <header className="usa-card__header">
                    <h3 className="usa-card__heading">Resource 1</h3>
                  </header>
                </div>
              </li>
              <li className="usa-card tablet:grid-col-4 mobile-lg:grid-col-12 resource-card">
                <div className="usa-card__container">
                  <header className="usa-card__header">
                    <h3 className="usa-card__heading">Resource 1</h3>
                  </header>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </>
  )
}

export default SplashPage
