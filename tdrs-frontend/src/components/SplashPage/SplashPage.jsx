import React, { useEffect, useRef } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Navigate } from 'react-router-dom'

import { setMockLoginState } from '../../actions/auth'

import loginLogo from '../../assets/login-gov-logo.svg'
import Button from '../Button'
import ResourceCards from '../ResourceCards'

/**
 * SplashPage renders the Welcome page for the TANF Data Portal
 * for an unauthenticated user. If a user logs in, they are automatically
 * redirected to `/profile`.
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
      window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login/dotgov`
    }
  }

  const signInWithAMS = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login/ams`
  }

  useEffect(() => {
    if (isInactive) {
      setTimeout(() => alertRef?.current?.focus(), 2)
    }
  }, [alertRef, isInactive])

  // Generate a random index for the splash page on every refresh
  const randomIndex = () => {
    return Math.floor(Math.random() * 3 + 1)
  }

  // Pa11y is not testing out authentication logic, by passing all auth checks
  // during Pa11y tests allows us to just point to a page in the config like
  // we have been doing.
  if (authenticated && !process.env.REACT_APP_PA11Y_TEST) {
    return <Navigate to="/home" />
  }

  if (authLoading) {
    return null
  }

  return (
    <>
      <section
        className={`usa-hero usa-hero${randomIndex()}`}
        aria-label="Introduction"
      >
        <div className="grid-container-widescreen">
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
              className="width-full"
              type="button"
              id="loginDotGovSignIn"
              onClick={signInWithLoginDotGov}
            >
              <div>
                Sign in with
                <img
                  className="mobile:margin-x-auto mobile:padding-top-1 mobile:margin-0 mobile:padding-top-0 width-15 padding-left-1"
                  src={loginLogo}
                  alt="Login.gov"
                />
                &nbsp; for grantees
              </div>
              <span className="visually-hidden">Opens in a new website</span>
            </Button>
            <Button
              className="width-full margin-top-3"
              type="button"
              id="acfAmsSignIn"
              onClick={signInWithAMS}
            >
              <div>Sign in with ACF AMS for ACF staff</div>
              <span className="visually-hidden">Opens in a new website</span>
            </Button>
          </div>
        </div>
      </section>
      <div class="grid-container-widescreen">
        <ResourceCards />
      </div>
    </>
  )
}

export default SplashPage
