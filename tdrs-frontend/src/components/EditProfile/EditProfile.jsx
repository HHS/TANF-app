import React, { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'

function EditProfile() {
  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })
  const [errors, setErrors] = useState({})

  const sttsLoading = useSelector((state) => state.stts.loading)
  const stts = useSelector((state) => state.stts.stts)
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchStts())
  }, [dispatch])

  const validateInputs = ({ name, value }) => {
    if (value.length < 1)
      return setErrors({
        ...errors,
        [name]: 'You need at least 1 character',
      })
    return setErrors({})
  }

  return (
    <div className="grid-container">
      <h1 className="request-access-header font-serif-2xl">Request Access</h1>
      <p className="request-access-secondary">
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <form className="usa-form">
        <div
          className={`usa-form-group ${
            errors['first-name'] ? 'usa-form-group--error' : ''
          }`}
        >
          <label
            className={`usa-label ${
              errors['first-name'] ? 'usa-label--error' : ''
            }`}
            htmlFor="first-name"
          >
            First name
            {errors['first-name'] && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors['first-name']}
              </span>
            )}
            <input
              className={`usa-input ${
                errors['first-name'] ? 'usa-input--error' : ''
              }`}
              id="first-name"
              name="first-name"
              type="text"
              required
              aria-required="true"
              value={profileInfo.firstName}
              onChange={({ target }) => {
                validateInputs(target)
                setProfileInfo({ ...profileInfo, firstName: target.value })
              }}
            />
          </label>
        </div>
        <div
          className={`usa-form-group ${
            errors['last-name'] ? 'usa-form-group--error' : ''
          }`}
        >
          <label
            className={`usa-label ${
              errors['last-name'] ? 'usa-label--error' : ''
            }`}
            htmlFor="last-name"
          >
            Last name
            {errors['last-name'] && (
              <span
                className="usa-error-message"
                id="input-error-message"
                role="alert"
              >
                {errors['last-name']}
              </span>
            )}
            <input
              className={`usa-input ${
                errors['last-name'] ? 'usa-input--error' : ''
              }`}
              id="last-name"
              name="last-name"
              type="text"
              required
              aria-required="true"
              value={profileInfo.lastName}
              onChange={({ target }) => {
                validateInputs(target)
                setProfileInfo({ ...profileInfo, lastName: target.value })
              }}
            />
          </label>
        </div>
        <div
          className={`usa-form-group ${
            errors.stt ? 'usa-form-group--error' : ''
          }`}
        >
          {/* I am disabling this rule here because the <Select> component does have an input with an id of 'stt'
            but only once it's rendered.
          */}
          {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
          <label className="usa-label" htmlFor="stt">
            Associated State, Tribe, or Territory
            <div className="usa-combo-box">
              <select
                className="usa-select usa-combo-box__select"
                name="stt"
                id="fruit"
              >
                {stts.map((stt) => (
                  <option value={stt.name.toLowerCase()}>{stt.name}</option>
                ))}
              </select>
            </div>
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
