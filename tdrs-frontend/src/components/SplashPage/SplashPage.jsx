import React from 'react'
import { useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'

function SplashPage() {
  const authenticated = useSelector((state) => state.auth.authenticated)
  const authLoading = useSelector((state) => state.auth.loading)

  const handleClick = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/login/oidc`
  }

  if (authenticated) {
    return <Redirect to="/dashboard" />
  }

  if (authLoading) {
    return null
  }

  return (
    <main id="main-content">
      <section className="usa-hero" aria-label="Introduction">
        <div className="grid-container">
          <div className="usa-hero__callout">
            <h1 className="usa-hero__heading">
              <span className="usa-hero__heading--alt margin-bottom-5">
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
            <button
              className="usa-button sign-in-button"
              type="button"
              size="big"
              onClick={handleClick}
            >
              Sign in with Login.gov
              <span className="visually-hidden">Opens in a new website</span>
            </button>
          </div>
        </div>
      </section>

      <section className="grid-container usa-section">
        <div className="grid-row grid-gap">
          <div className="tablet:grid-col-4">
            <h2 className="resources-header font-heading-2xl margin-top-0 tablet:margin-bottom-0">
              Featured TANF Resources
            </h2>
            <div className="font-heading-3xs resource-info__secondary">
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
                    <h2 className="usa-card__heading">Resource 1</h2>
                  </header>
                </div>
              </li>
              <li className="usa-card tablet:grid-col-4 mobile-lg:grid-col-12 resource-card">
                <div className="usa-card__container">
                  <header className="usa-card__header">
                    <h2 className="usa-card__heading">Resource 1</h2>
                  </header>
                </div>
              </li>
              <li className="usa-card tablet:grid-col-4 mobile-lg:grid-col-12 resource-card">
                <div className="usa-card__container">
                  <header className="usa-card__header">
                    <h2 className="usa-card__heading">Resource 1</h2>
                  </header>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  )
}

export default SplashPage
