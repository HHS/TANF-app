import React, { useRef, useState } from 'react'
import Button from '../Button'
import { useDispatch } from 'react-redux'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'
import JurisdictionSelector from './JurisdictionSelector'
import JurisdictionLocationInfo from '../Profile/JurisdictionLocationInfo'
import RegionSelector from './RegionSelector'
import FRASelector from './FRASelector'
import '../../assets/Profile.scss'

// TODO: random white space is appearing under the footer on this page - figure out why
function RequestAccessForm({
  user,
  sttList,
  editMode = false,
  initialValues = {},
  onCancel,
}) {
  const errorRef = useRef(null)

  const isAMSUser = user?.email?.includes('@acf.hhs.gov')
  //const isAMSUser = true
  const primaryRole = user?.roles?.[0]
  //const primaryRole = 'Regional Staff'

  const [errors, setErrors] = useState({})
  const [profileInfo, setProfileInfo] = useState({
    firstName: initialValues.firstName || '',
    lastName: initialValues.lastName || '',
    stt: initialValues.stt || '',
    hasFRAAccess: initialValues.hasFRAAccess ?? (isAMSUser ? false : null),
    ...(isAMSUser && { regions: initialValues.regions || new Set() }),
  })
  const [originalData] = useState(profileInfo)

  const dispatch = useDispatch()
  const [touched, setTouched] = useState({})
  const fieldErrorKeys = Object.keys(errors).filter((key) => key !== 'form')
  const hasFieldErrors =
    fieldErrorKeys.length > 0 && Object.keys(touched).length > 0

  const showErrorSummary = hasFieldErrors || !!errors.form

  const [jurisdictionType, setJurisdictionTypeInputValue] = useState(
    initialValues.jurisdictionType || 'state'
  )

  const regionError = 'At least one Region is required'

  console.log('User:', user)

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
    if (hasFieldErrors || errors.hasFRAAccess) {
      const { hasFRAAccess: removedError, ...rest } = errors
      const error = validation('hasFRAAccess', hasFRAAccess)

      setErrors({
        ...rest,
        ...(error && { hasFRAAccess: error }),
      })
    }
  }

  const handleChange = ({ name, value }) => {
    // Clear form error if present on any change
    if (errors.form) {
      const { form, ...rest } = errors
      setErrors(rest)
    }

    // Remove error for this field if present
    if (errors[name]) {
      const { [name]: removedError, ...rest } = errors
      setErrors(rest)
    }

    setTouched((prev) => ({ ...prev, [name]: true }))
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

    if (editMode) {
      const hasChanges = Object.keys(profileInfo).some((key) => {
        if (typeof profileInfo[key] === 'object') {
          return (
            JSON.stringify(profileInfo[key]) !==
            JSON.stringify(originalData[key])
          )
        }
        return profileInfo[key] !== originalData[key]
      })

      if (!hasChanges) {
        setErrors({ form: 'No changes have been made.' })
        setTimeout(() => errorRef.current?.focus(), 0)
        return
      }

      // TODO: mock call to new API eventually
      // TODO: Implement API call to update user profile when editing
    }

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

  const ReadOnlyRow = ({ label, value }) => (
    <div className="read-only-row">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  )

  const renderRegionSelector = (
    <div className="grid-container">
      <RegionSelector
        setErrors={setErrors}
        errors={errors}
        setTouched={setTouched}
        touched={touched}
        setProfileInfo={setProfileInfo}
        profileInfo={profileInfo}
        displayingError={hasFieldErrors}
        validateRegions={validateRegions}
        regionError={regionError}
      />
    </div>
  )

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
            showErrorSummary ? 'display-block' : 'display-none'
          }`}
          ref={errorRef}
          tabIndex="-1"
          role="alert"
        >
          {errors.form
            ? errors.form
            : `There are ${Object.keys(errors).length} errors in this form`}
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
        {editMode ? (
          isAMSUser ? (
            renderRegionSelector
          ) : (
            <div>
              <hr className="form-section-divider" />
              {/* <hr className="margin-right-4 margin-top-3 margin-bottom-2" /> */}
              <ReadOnlyRow label="User Type" value={primaryRole?.name} />
              <ReadOnlyRow
                label="Jurisdiction Type"
                value={
                  (jurisdictionType?.charAt(0)?.toUpperCase() ?? '') +
                  (jurisdictionType?.slice(1) ?? '')
                }
              />
              <JurisdictionLocationInfo
                jurisdictionType={jurisdictionType}
                locationName={profileInfo.stt}
                formType={'access request'}
              />
              <hr className="form-section-divider" />
            </div>
          )
        ) : (
          <div className="grid-container">
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
            {isAMSUser && renderRegionSelector}
          </div>
        )}
        {jurisdictionType !== 'tribe' && !isAMSUser && (
          <FRASelector
            hasFRAAccess={profileInfo.hasFRAAccess}
            setHasFRAAccess={setHasFRAAccess}
            error={errors.hasFRAAccess}
          />
        )}
        {!editMode ? (
          <Button type="submit" className="width-full request-access-button">
            Request Access
          </Button>
        ) : (
          <div className="usa-button-group margin-top-4">
            <button
              type="submit"
              className="usa-button"
              style={{ minWidth: '300px' }}
            >
              Save Changes
            </button>
            <button
              type="button"
              className="usa-button margin-left-2"
              style={{ minWidth: '200px' }}
              onClick={onCancel}
            >
              Cancel
            </button>
          </div>
        )}
      </form>
    </div>
  )
}

export default RequestAccessForm
