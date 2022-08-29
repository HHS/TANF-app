import React from 'react'
import { useSelector } from 'react-redux'

import ACFLogo from '../../assets/ACFLogo.svg'

function Footer() {
  const authenticated = useSelector((state) => state.auth.authenticated)
  return (
    <footer className="usa-footer usa-footer--slim">
      <div className="usa-footer__primary-section">
        <div className="grid-container-widescreen grid-row">
          <div className="mobile-lg:grid-col-8">
            <nav className="usa-footer__nav" aria-label="Footer navigation">
              <ul className="grid-row grid-gap">
                <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                  <a
                    className="usa-footer__primary-link"
                    href="https://www.acf.hhs.gov/privacy-policy"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Privacy policy
                  </a>
                </li>
                {authenticated ? (
                  <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                    <a
                      className="usa-footer__primary-link"
                      href="/site-map"
                      target="_self"
                      rel="noopener noreferrer"
                    >
                      Site Map
                    </a>
                  </li>
                ) : null}
              </ul>
              <ul className="grid-row">
                <li className="mobile-lg:grid-col-6 desktop:grid-col-auto usa-footer__primary-content">
                  <a
                    className="usa-footer__primary-link"
                    href="https://www.hhs.gov/vulnerability-disclosure-policy/index.html"
                    target="_blank"
                    rel="noreferrer"
                  >
                    Vulnerability Disclosure Policy
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
      <div className="usa-footer__secondary-section">
        <div className="grid-container-widescreen">
          <div className="usa-footer__logo margin-left-neg-205">
            <div className="grid-col-auto">
              <img
                className="mobile-lg:maxw-mobile mobile:width-mobile"
                alt="Administration for Children and Families, Office of Family Assistance"
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
