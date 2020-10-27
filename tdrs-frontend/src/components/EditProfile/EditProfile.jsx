import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Redirect } from 'react-router-dom'
import axios from 'axios'

import { fetchSttList } from '../../actions/sttList'
import Button from '../Button'
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
  const sttList = useSelector((state) => state.stts.sttList)
  const dispatch = useDispatch()

  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })

  const [returnedUser, setReturnedUser] = useState(null)

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

  const handleBlur = (evt) => {
    const { name, value } = evt.target

    const { [name]: removedError, ...rest } = errors

    const error = validation(name, value)

    setErrors({
      ...rest,
      ...(error && { [name]: touched[name] && error }),
    })
  }

  const handleSubmit = async (evt) => {
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
      const {
        firstName,
        lastName,
        stt: { id },
      } = profileInfo
      try {
        const URL = `${process.env.REACT_APP_BACKEND_URL}/users/set_profile/`
        const user = {
          first_name: firstName,
          last_name: lastName,
          stt: { id },
        }
        const { data } = await axios.patch(URL, user, {
          withCredentials: true,
        })
        if (data) {
          setReturnedUser(true)
        } else {
          setReturnedUser(false)
        }
      } catch (error) {
        return console.log('error', error)
      }
    }

    return true
  }

  if (returnedUser) {
    return <Redirect to="/unassigned" />
  }

  return (
    <div className="grid-container">
      <h1 className="font-serif-2xl" style={{ fontWeight: 400 }}>
        Request Access
      </h1>
      <p>
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <form className="usa-form" onSubmit={handleSubmit}>
        <div
          className={`usa-form-group ${
            errors.firstName ? 'usa-form-group--error' : ''
          }`}
        >
          <label
            className={`usa-label ${
              errors.firstName ? 'usa-label--error' : ''
            }`}
            htmlFor="firstName"
          >
            First name
            {errors.firstName && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors.firstName}
              </span>
            )}
            <input
              className={`usa-input ${
                errors.firstName ? 'usa-input--error' : ''
              }`}
              id="firstName"
              name="firstName"
              type="text"
              aria-required="true"
              value={profileInfo.firstName}
              onChange={({ target: { value } }) => {
                setProfileInfo({ ...profileInfo, firstName: value })
              }}
              onBlur={handleBlur}
            />
          </label>
        </div>
        <div
          className={`usa-form-group ${
            errors.lastName ? 'usa-form-group--error' : ''
          }`}
        >
          <label
            className={`usa-label ${errors.lastName ? 'usa-label--error' : ''}`}
            htmlFor="lastName"
          >
            Last name
            {errors.lastName && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors.lastName}
              </span>
            )}
            <input
              className={`usa-input ${
                errors.lastName ? 'usa-input--error' : ''
              }`}
              id="lastName"
              name="lastName"
              type="text"
              aria-required="true"
              value={profileInfo.lastName}
              onChange={({ target: { value } }) => {
                setProfileInfo({ ...profileInfo, lastName: value })
              }}
              onBlur={handleBlur}
            />
          </label>
        </div>
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
    </div>
  )
}

export default EditProfile
