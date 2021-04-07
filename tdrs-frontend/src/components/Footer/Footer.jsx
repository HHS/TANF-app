import React from 'react'

import ACFLogo from '../../assets/ACFLogo.svg'

function Footer() {
  return (
    <footer className="usa-footer usa-footer--slim">
      <div className="usa-footer__primary-section">
        <div className="usa-footer__primary-container grid-row">
          <div className="mobile-lg:grid-col-8">
            <nav className="usa-footer__nav" aria-label="Footer navigation">
              <ul className="grid-row grid-gap">
                <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                  <a
                    className="usa-footer__primary-link"
                    href="https://www.acf.hhs.gov/privacy-policy"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Privacy policy
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
      <div className="usa-footer__secondary-section">
        <div className="grid-container">
          <div className="usa-footer__logo grid-row grid-gap-2">
            <div className="grid-col-auto">
              <img
                className="mobile-lg:maxw-mobile mobile:width-mobile"
                alt="Administration for Children and Families Logo"
                src={ACFLogo}
              />
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer
