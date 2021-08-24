import React from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useSelector } from 'react-redux'

function Welcome() {
  const logOut = () => {
    window.location = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }
  const user = useSelector((state) => state.auth.user)
  const role = user?.roles
  const hasRole = Boolean(role?.length > 0)

  return (
    <div className="margin-top-5">
      {!hasRole ? (
        <p className="margin-top-1 margin-bottom-4">
          Your request for access is currently being reviewed by an OFA Admin.
          We'll send you an email when it's been approved.
        </p>
      ) : (
        <>
          <p className="margin-top-1 margin-bottom-4">
            You've been approved as a/an {role?.[0].name}. You'll be able to do
            the following in TDP:
          </p>
          <ul>
            {role?.[0]?.permissions?.map((permission) => (
              <li key={permission.id} id={permission.id}>
                {permission.name}
              </li>
            ))}
          </ul>
        </>
      )}
      <Button
        type="button"
        className="width-tablet margin-bottom-4"
        onClick={logOut}
      >
        <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
        Sign Out
      </Button>
    </div>
  )
}

export default Welcome
