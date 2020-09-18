import React from 'react'

import ACFLogo from '../../assets/ACFLogo.svg'

function Footer() {
  return (
    <footer className="usa-footer usa-footer--slim">
      <div className="usa-footer__secondary-section">
        <div className="grid-container">
          <div className="usa-footer__logo grid-row grid-gap-2">
            <div className="grid-col-auto">
              <img
                className="maxw-mobile usa-footer__logo-img"
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
