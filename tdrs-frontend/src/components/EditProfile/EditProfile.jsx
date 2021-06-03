import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'

import { requestAccess } from '../../actions/requestAccess'
import { setAlert } from '../../actions/alert'
import { ALERT_ERROR } from '../Alert'

import Button from '../Button'
import FormGroup from '../FormGroup'

import STTComboBox from '../STTComboBox'
import { useEventLogger } from '../../utils/eventLogger'
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
 * EditProfile renders the Request Access form for creating a profile.
 * EditProfile dispatches event fetchStts to get a list of STTs to render
 * inside of the combo box.
 *
 * EditProfile renders a form for a user to request access to the application.
 * There is an input for first and last name and a combo box to select
 *  an associated STT.
 */

function EditProfile() {
  const errorRef = useRef(null)
  const requestedAccess = useSelector(
    (state) => state.requestAccess.requestAccess
  )
  const requestAccessError = useSelector((state) => state.requestAccess.error)
  const sttAssigned = useSelector((state) => state.auth.user.stt)
  const sttList = useSelector((state) => state.stts.sttList)

  const dispatch = useDispatch()

  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })

  const [errors, setErrors] = useState({})

  const [touched, setTouched] = useState({})

  const logger = useEventLogger()

  useEffect(() => {
    if (requestAccessError) {
      dispatch(
        setAlert({ heading: requestAccessError.message, type: ALERT_ERROR })
      )
      logger.error(requestAccessError.message)
    }
  }, [dispatch, requestAccessError, logger])

  const setStt = (sttName) => {
    setProfileInfo((currentState) => ({
      ...currentState,
      stt: sttName,
    }))
  }

  const handleChange = ({ name, value }) => {
    setProfileInfo({ ...profileInfo, [name]: value })
  }

  const handleBlur = (evt) => {
    const { name, value } = evt.target

    const { [name]: removedError, ...rest } = errors

    const error = validation(name, value)

    setErrors({
      ...rest,
      ...(error && { [name]: touched[name] && error }),
    })
  }
  const handleSubmit = (evt) => {
    evt.preventDefault()

    // validate the form
    const formValidation = Object.keys(profileInfo).reduce(
      (acc, key) => {
        const newError = validation(key, profileInfo[key])
        const newTouched = { [key]: true }
        return {
          errors: {
            ...acc.errors,
            ...(newError && { [key]: newError }),
          },
          touched: {
            ...acc.touched,
            ...newTouched,
          },
        }
      },
      {
        errors: { ...errors },
        touched: { ...touched },
      }
    )
    setErrors(formValidation.errors)
    setTouched(formValidation.touched)

    if (!Object.values(formValidation.errors).length) {
      return dispatch(
        requestAccess({
          ...profileInfo,
          stt: sttList.find((stt) => stt.name === profileInfo.stt),
        })
      )
    }
    return setTimeout(() => errorRef.current.focus(), 0)
  }

  if (requestedAccess && sttAssigned) {
    return <Redirect to="/request" />
  }

  return (
    <>
      <p className="margin-top-1 margin-bottom-4">
        Please enter your information to request access from an OFA
        administrator
      </p>
      <form className="usa-form" onSubmit={handleSubmit}>
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
        <FormGroup
          error={errors.firstName}
          name="firstName"
          label="First Name"
          inputValue={profileInfo.firstName}
          handleChange={handleChange}
          handleBlur={handleBlur}
        />
        <FormGroup
          error={errors.lastName}
          name="lastName"
          label="Last Name"
          inputValue={profileInfo.lastName}
          handleChange={handleChange}
          handleBlur={handleBlur}
        />
        <div
          className={`usa-form-group ${
            errors.stt ? 'usa-form-group--error' : ''
          }`}
        >
          <STTComboBox
            selectStt={setStt}
            error={Boolean(errors.stt)}
            selectedStt={profileInfo?.stt}
            handleBlur={handleBlur}
          />
        </div>
        <Button type="submit" className="width-full request-access-button">
          Request Access
        </Button>
      </form>
    </>
  )
}

export default EditProfile
