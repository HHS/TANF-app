import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import comboBox from 'uswds/src/js/components/combo-box'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'

export const validation = (fieldName, fieldValue) => {
  if (fieldValue.trim() === '') {
    return `${fieldName} is required`
  }
  return null
}

function EditProfile() {
  const stts = useSelector((state) => state.stts.stts)
  const dispatch = useDispatch()

  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })
  const [errors, setErrors] = React.useState({})

  const [touched, setTouched] = React.useState({})

  useEffect(() => {
    dispatch(fetchStts())
    comboBox.init()
  }, [dispatch])

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
  }

  return (
    <div className="grid-container">
      <h1 className="request-access-header font-serif-2xl">Request Access</h1>
      <p className="request-access-secondary">
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
              onChange={({ target }) => {
                setProfileInfo({ ...profileInfo, firstName: target.value })
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
              onChange={({ target }) => {
                setProfileInfo({ ...profileInfo, lastName: target.value })
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
          <label className="usa-label" htmlFor="sttList">
            Associated State, Tribe, or Territory
            {errors.stt && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors.stt}
              </span>
            )}
            <div className="usa-combo-box">
              <select
                className="usa-select"
                name="sttList"
                id="sttList"
                data-value={profileInfo.stt}
                // value={profileInfo.stt}
                // onChange={(e) =>
                //   setProfileInfo({
                //     ...profileInfo,
                //     stt: e.target.value,
                //   })
                // }
              >
                {stts.map((stt) => (
                  <option key={stt.id} value={stt.name.toLowerCase()}>
                    {stt.name}
                  </option>
                ))}
              </select>
            </div>
            {/* <Button label="Hello Button" /> */}
          </label>
        </div>
        <Button type="submit" size="big" className="request-access-button">
          Request Access
        </Button>
      </form>
    </div>
  )
}

export default EditProfile
