import React, { useState, useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'

import { fetchSttList } from '../../actions/sttList'
import { requestAccess } from '../../actions/requestAccess'
import Button from '../Button'
import FormGroup from '../FormGroup'
import ComboBox from '../ComboBox'

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
  const sttList = useSelector((state) => state.stts.sttList)
  const requestedAccess = useSelector(
    (state) => state.requestAccess.requestAccess
  )

  const dispatch = useDispatch()

  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })

  const [errors, setErrors] = useState({})

  const [touched, setTouched] = useState({})

  useEffect(() => {
    dispatch(fetchSttList())
  }, [dispatch])

  const setStt = (sttName) => {
    let selectedStt = sttList.find((stt) => sttName === stt.name.toLowerCase())
    if (!selectedStt) selectedStt = ''
    setProfileInfo({ ...profileInfo, stt: selectedStt })
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
      return dispatch(requestAccess(profileInfo))
    }
    return setTimeout(() => errorRef.current.focus(), 10)
  }

  if (requestedAccess) {
    setTimeout(() => errorRef.current.focus(), 0)
    return <Redirect to="/unassigned" />
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
              <ComboBox
                name="stt"
                error={errors.stt}
                handleSelect={setStt}
                selected={
                    profileInfo.stt &&
                        profileInfo.stt.name &&
                        profileInfo.stt.name.toLowerCase()
                }
                handleBlur={handleBlur}
                placeholder="- Select or Search -"
              >
                <option value="">Select an STT</option>
                {sttList.map((stt) => (
                    <option
                      className="sttOption"
                      key={stt.id}
                      value={stt.name.toLowerCase()}
                    >
                      {stt.name}
                    </option>
                ))}
              </ComboBox>
            </div>
            <Button type="submit" className="width-full request-access-button">
              Request Access
            </Button>
          </form>
        </>
    )
}

export default EditProfile
