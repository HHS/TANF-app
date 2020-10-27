import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import Button from '../Button'

function Unassigned() {
  return (
    <div className="grid-container margin-top-3">
      <ul className="usa-card-group">
        <li className="tablet:grid-col-6 usa-card">
          <div className="usa-card__container">
            <header className="usa-card__header">
              <h1 className="font-serif-2xl" style={{ fontWeight: 400 }}>
                Request Submitted
              </h1>
            </header>
            <div className="usa-card__body">
              <p>
                An administrator will be in touch soon to confirm your access!
              </p>
            </div>
            <div className="usa-card__footer">
              <Button className="width-full">
                <FontAwesomeIcon
                  className="margin-right-1"
                  icon={faSignOutAlt}
                />
                Sign Out
              </Button>
            </div>
          </div>
        </li>
      </ul>
    </div>
  )
}

export default Unassigned
