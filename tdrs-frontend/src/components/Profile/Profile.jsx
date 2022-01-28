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
  const errorRef = useRef(null)
  const requestedAccess = useSelector(
    (state) => state.requestAccess.requestAccess
  )
  const requestAccessError = useSelector((state) => state.requestAccess.error)
  const sttAssigned = useSelector((state) => state.auth.user.stt)
  const sttList = useSelector((state) => state.stts.sttList)
  const user = useSelector((state) => state.auth.user)

  const dispatch = useDispatch()

  const [errors, setErrors] = useState({})

  const [touched, setTouched] = useState({})

  const logger = useEventLogger()

  const isAMSUser = false

  useEffect(() => {
    if (requestAccessError) {
      dispatch(
        setAlert({ heading: requestAccessError.message, type: ALERT_ERROR })
      )
      logger.error(requestAccessError.message)
    }
  }, [dispatch, requestAccessError, logger])

  if (requestedAccess && sttAssigned) {
    return <Redirect to="/home" />
  }

  return (
    <div className="usa-prose">
      <div
        className={`usa-error-message ${
          !!Object.keys(errors).length && !!Object.keys(touched).length
            ? 'display-block'
            : 'display-none'
        }`}
        ref={errorRef}
        tabIndex="-1"
        role="alert"
      >
        There are {Object.keys(errors).length} errors in this form
      </div>
      <div>
        <p className="text-bold">
          {user.first_name} {user.last_name}
        </p>
        <p>{user.stt.name}</p>
        <p>{user.email}</p>
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
