import React from 'react'

import smallFlag from 'uswds/dist/img/us_flag_small.png'
import govLogo from 'uswds/dist/img/icon-dot-gov.svg'
import httpsLogo from 'uswds/dist/img/icon-https.svg'
import lock from 'uswds/dist/img/lock.svg'

function GovBanner() {
  return (
    <section className="usa-banner" aria-label="Official government website">
      {' '}
      <div className="usa-accordion">
        <header className="usa-banner__header">
          <div className="usa-banner__inner">
            <div className="grid-col-auto">
              <img
                className="usa-banner__header-flag"
                src={smallFlag}
                alt="U.S. flag"
              />
            </div>
            <div className="grid-col-fill tablet:grid-col-auto">
              <p className="usa-banner__header-text">
                A DEMO website of the United States government
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
                src={govLogo}
                alt=".gov logo"
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
                src={httpsLogo}
                alt="Https"
              />
              <div className="usa-media-block__body">
                <p>
                  <strong>Secure .gov websites use HTTPS</strong>
                  <br />A <strong>lock</strong> (
                  <span className="icon-lock">
                    <img
                      className="usa-banner__lock-image"
                      src={lock}
                      alt="lock"
                    />
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
  )
}

export default GovBanner
