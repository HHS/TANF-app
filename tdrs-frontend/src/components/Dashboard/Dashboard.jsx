import React from 'react'
import { useSelector } from 'react-redux'

/**
 * This component renders for a user who just logged in.
 * It renders a sign-out button and when clicked,
 * the user is redirected to the backend's logout endpoint,
 * initiating the logout process.
 *
 * @param {object} email - a user's email address
 */
function Dashboard() {
  const user = useSelector((state) => state.auth.user.email)
  const handleClick = (event) => {
    event.preventDefault()
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }
  return (
    <div className="grid-container welcome">
      <div className="grid-row">
        <div className="grid-col-8">
          <h1>
            Welcome, <em>{user}</em>!
            <span role="img" aria-label="wave" aria-hidden="true">
              {' '}
              🎉
            </span>
          </h1>
        </div>
        <div className="grid-col-4">
          <button
            type="button"
            className="usa-button usa-button--big"
            onClick={handleClick}
          >
            Sign Out
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
