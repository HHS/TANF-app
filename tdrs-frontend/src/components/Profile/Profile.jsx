import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'

import { setAlert } from '../../actions/alert'
import { ALERT_ERROR } from '../Alert'

import { useEventLogger } from '../../utils/eventLogger'
import loginLogo from '../../assets/login-gov-logo.svg'
import Button from '../Button'

/**
 *
 * @param {string} fieldName - The name of the element that is being validated
 * @param {string || object} fieldValue - The value of the field. A string from
 * First Name and Last Name.
 * The STT fieldValue is either a string or an object if there is a selected
 * STT.
 */
export const validation = (fieldName, fieldValue) => {
  let field
  switch (fieldName) {
    case 'firstName':
      field = 'First Name'
      break
    case 'lastName':
      field = 'Last Name'
      break
    case 'stt':
      field = 'A state, tribe, or territory'
      break
    default:
      field = ''
  }
  if (typeof fieldValue === 'string' && fieldValue.trim() === '') {
    return `${field} is required`
  }
  return null
}

/**
 * Profile renders the Request Access form for creating a profile.
 * Profile dispatches event fetchStts to get a list of STTs to render
 * inside of the combo box.
 *
 * Profile renders a form for a user to request access to the application.
 * There is an input for first and last name and a combo box to select
 *  an associated STT.
 */

function Profile() {
  const user = useSelector((state) => state.auth.user)
  const hasRoles = user.roles.length > 0
  const missingAccessRequest = !Boolean(user?.access_request)
  const isAccessRequestPending = Boolean(user?.access_request) && !hasRoles

  const isAMSUser = false

  if (missingAccessRequest) {
    return <Redirect to="/home" />
  }

  return (
    <div className="usa-prose">
      {isAccessRequestPending && (
        <div className="usa-alert usa-alert--info">
          <div className="usa-alert__body">
            <p className="usa-alert__text">
              Your request for access is currently being reviewed by an OFA
              Admin. We’ll send you an email when it’s been approved.
            </p>
          </div>
        </div>
      )}
      <div>
        <p className="text-bold">
          {user?.first_name} {user?.last_name}
        </p>
        <p>{user?.stt?.name}</p>
        <p>{user?.email}</p>
      </div>
      <div className="margin-top-5">
        <p className="text-bold">Email and Password</p>

        {isAMSUser ? (
          <p>
            You will receive all communications from the TANF Data Portal via
            your ACF email address.
          </p>
        ) : (
          <>
            <p>
              You will receive all communications from the TANF Data Portal via
              the email address you registered with Login.gov. Your email or
              password can be managed via Login.gov
            </p>
            <Button
              className="sign-in-button"
              type="button"
              id="loginDotGovSignIn"
              onClick={(event) => {
                event.preventDefault()
                window.location.href =
                  'https://idp.int.identitysandbox.gov/account'
              }}
            >
              <div className="mobile:margin-x-auto mobile-lg:margin-0">
                Manage Your Account at{' '}
                <img
                  className="mobile:margin-x-auto mobile:padding-top-1 mobile-lg:margin-0 mobile-lg:padding-top-0 width-15 padding-left-1"
                  src={loginLogo}
                  alt="Login.gov"
                />
              </div>
              <span className="visually-hidden">Opens in a new website</span>
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

export default Profile
