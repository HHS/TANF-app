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
    <>
      <div className="maxw-mobile-lg">
        <p className="margin-top-1 margin-bottom-4">
          An administrator will be in touch soon to confirm your access!
        </p>
        <Button className="width-full" type="button" onClick={signOut}>
          <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
          Sign Out
        </Button>
      </div>
    </>
  )
}

export default Request
