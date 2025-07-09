import React, { useRef, useState } from 'react'
import Button from '../Button'
import { useDispatch } from 'react-redux'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'
import JurisdictionSelector from './JurisdictionSelector'
import RegionSelector from './RegionSelector'
import FRASelector from './FRASelector'

function RequestAccessForm({ user, sttList }) {
  const errorRef = useRef(null)

  const isAMSUser = user?.email?.includes('@acf.hhs.gov')

  const [errors, setErrors] = useState({})
  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
    hasFRAAccess: isAMSUser ? false : null,
  })
  const dispatch = useDispatch()
  const [touched, setTouched] = useState({})
  const displayingError =
    !!Object.keys(errors).length && !!Object.keys(touched).length

  const [jurisdictionType, setJurisdictionTypeInputValue] = useState('state')

  const regionError = 'At least one Region is required'

  const validateRegions = (regions) => {
    if (regions?.size === 0) {
      return regionError
    }
    return null
  }

  const validation = (fieldName, fieldValue) => {
    const field = {
      firstName: 'First Name',
      lastName: 'Last Name',
      stt: !isAMSUser && 'A state, tribe, or territory',
      hasFRAAccess: 'Yes or No response',
    }[fieldName]

    if (
      Boolean(field) &&
      ((fieldName === 'hasFRAAccess' && fieldValue === null) ||
        (typeof fieldValue === 'string' && fieldValue.trim() === ''))
    ) {
      return `${field} is required`
    }
    return null
  }

  const setJurisdictionType = (val) => {
    setStt('')
    setJurisdictionTypeInputValue(val)
    if (val === 'tribe') {
      setHasFRAAccess(false)
    } else {
      setHasFRAAccess(null)
    }
  }

  const setStt = (sttName) => {
    setProfileInfo((currentState) => ({
      ...currentState,
      stt: sttName,
    }))
  }

  const setHasFRAAccess = (hasFRAAccess) => {
    setProfileInfo((currentState) => ({
      ...currentState,
      hasFRAAccess: hasFRAAccess,
    }))

    // Remove errors when FRA Access is changed or hidden
    if (displayingError) {
      const { hasFRAAccess: removedError, ...rest } = errors
      const error = validation('hasFRAAccess', hasFRAAccess)

      setErrors({
        ...rest,
        ...(error && { hasFRAAccess: error }),
      })
    }
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
    const regionError = validateRegions(profileInfo.regions)

    const combinedErrors = {
      ...formValidation.errors,
      ...(regionError && { regions: regionError }),
    }
    const combinedTouched = {
      ...formValidation.touched,
      ...(regionError && { regions: true }),
    }

    setErrors(combinedErrors)
    setTouched(combinedTouched)

    if (!Object.values(combinedErrors).length) {
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
            displayingError ? 'display-block' : 'display-none'
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
          <JurisdictionSelector setJurisdictionType={setJurisdictionType} />
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
        {isAMSUser && (
          <RegionSelector
            setErrors={setErrors}
            errors={errors}
            setTouched={setTouched}
            touched={touched}
            setProfileInfo={setProfileInfo}
            profileInfo={profileInfo}
            displayingError={displayingError}
            validateRegions={validateRegions}
            regionError={regionError}
          />
        )}
        {jurisdictionType !== 'tribe' && !isAMSUser && (
          <FRASelector
            hasFRAAccess={profileInfo.hasFRAAccess}
            setHasFRAAccess={setHasFRAAccess}
            error={errors.hasFRAAccess}
          />
        )}
        <Button type="submit" className="width-full request-access-button">
          Request Access
        </Button>
      </form>
    </div>
  )
}

export default RequestAccessForm
