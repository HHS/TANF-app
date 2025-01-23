import React, { useRef, useState } from 'react'
import Button from '../Button'
import { useDispatch } from 'react-redux'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'

function RequestAccessForm({ user, sttList }) {
  const errorRef = useRef(null)

  const [errors, setErrors] = useState({})
  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
    regions: new Set(),
  })
  const dispatch = useDispatch()
  const [touched, setTouched] = useState({})

  const [jurisdictionType, setJurisdictionTypeInputValue] = useState('state')
  const isAMSUser = user?.email?.includes('@acf.hhs.gov')

  const regionsNames = [
    'Boston',
    'New York',
    'Philadelphia',
    'Atlanta',
    'Chicago',
    'Dallas',
    'Kansas City',
    'Denver',
    'San Francisco',
    'Seattle',
  ]

  const handleRegionChange = (event, regionPK) => {
    const { name, checked } = event.target
    const { [name]: removedError, ...rest } = errors
    const newProfileInfo = { ...profileInfo }
    if (!checked && newProfileInfo.regions.has(regionPK)) {
      newProfileInfo.regions.delete(regionPK)
    } else {
      newProfileInfo.regions.add(regionPK)
    }

    const error = validation(name, newProfileInfo.regions)

    setErrors({
      ...rest,
      ...(error && { [name]: touched[name] && error }),
    })
    setProfileInfo({ ...newProfileInfo })
  }

  const validation = (fieldName, fieldValue) => {
    const field = {
      firstName: 'First Name',
      lastName: 'Last Name',
      stt: !isAMSUser && 'A state, tribe, or territory',
      regions: 'At least one Region',
    }[fieldName]

    if (
      (Boolean(field) &&
        typeof fieldValue === 'string' &&
        fieldValue.trim() === '') ||
      (fieldValue instanceof Set && fieldValue.size === 0)
    ) {
      return `${field} is required`
    }
    return null
  }

  const setJurisdictionType = (val) => {
    setStt('')
    setJurisdictionTypeInputValue(val)
  }

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

  return (
    <div className="margin-top-5 margin-bottom-5">
      <p className="margin-top-1 margin-bottom-4">
        Please enter your information to request access from an OFA
        administrator
      </p>
      <p>Fields marked with an asterisk (*) are required.</p>
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
        {!isAMSUser && (
          <div className="usa-form-group">
            <fieldset className="usa-fieldset">
              <legend className="usa-label text-bold">Jurisdiction Type</legend>
              <div className="usa-radio">
                <input
                  className="usa-radio__input"
                  id="state"
                  type="radio"
                  name="jurisdictionType"
                  value="state"
                  defaultChecked
                  onChange={() => setJurisdictionType('state')}
                />
                <label className="usa-radio__label" htmlFor="state">
                  State
                </label>
              </div>
              <div className="usa-radio">
                <input
                  className="usa-radio__input"
                  id="tribe"
                  type="radio"
                  name="jurisdictionType"
                  value="tribe"
                  onChange={() => setJurisdictionType('tribe')}
                />
                <label className="usa-radio__label" htmlFor="tribe">
                  Tribe
                </label>
              </div>
              <div className="usa-radio">
                <input
                  className="usa-radio__input"
                  id="territory"
                  type="radio"
                  name="jurisdictionType"
                  value="territory"
                  onChange={() => setJurisdictionType('territory')}
                />
                <label className="usa-radio__label" htmlFor="territory">
                  Territory
                </label>
              </div>
            </fieldset>
          </div>
        )}
        {jurisdictionType && !isAMSUser && (
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
              sttType={jurisdictionType}
            />
          </div>
        )}
        {/* TODO: change !isAMSUser to isAMSUser */}
        {!isAMSUser && (
          <div
            className={`usa-form-group ${errors.regions ? 'usa-form-group--error' : ''}`}
          >
            <fieldset className="usa-fieldset">
              <legend className="usa-label text-bold">Region(s)*</legend>
              <div>
                Need help?&nbsp;
                <a href="google.com">Lookup region by location.</a>
              </div>
              {errors.regions && (
                <span
                  className="usa-error-message"
                  id={`regions-error-message`}
                >
                  {errors.regions}
                </span>
              )}
              {regionsNames.map((region, index) => {
                return (
                  <div className="usa-checkbox">
                    <input
                      className={`usa-checkbox__input ${errors.regions ? 'usa-input--error' : ''}`}
                      id={region}
                      type="checkbox"
                      name="regions"
                      value={region}
                      onChange={(event) => handleRegionChange(event, index + 1)}
                    />
                    <label
                      className={`usa-checkbox__label ${errors.regions ? 'usa-input--error' : ''}`}
                      htmlFor={region}
                    >
                      Region {index + 1} ({region})
                    </label>
                  </div>
                )
              })}
            </fieldset>
          </div>
        )}
        <Button type="submit" className="width-full request-access-button">
          Request Access
        </Button>
      </form>
    </div>
  )
}

export default RequestAccessForm
