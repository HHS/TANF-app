import React from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import Button from '../Button'

function Request() {
  const signOut = (e) => {
    e.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  return (
    <div className="grid-container margin-top-3">
      <div className="maxw-mobile-lg">
        <h1 className="font-serif-2xl margin-bottom-0 text-normal">
          Request Submitted
        </h1>
        <p className="margin-top-1 margin-bottom-4">
          An administrator will be in touch soon to confirm your access!
        </p>
        <Button
          className="width-full request-access-button"
          type="button"
          onClick={signOut}
        >
          <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
          Sign Out
        </Button>
      </div>
    </div>
  )
}

export default Request
