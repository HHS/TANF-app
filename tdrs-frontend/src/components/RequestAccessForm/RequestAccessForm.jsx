import React, { useRef, useState, useEffect } from 'react'
import Button from '../Button'
import { useDispatch } from 'react-redux'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'
import JurisdictionSelector from './JurisdictionSelector'
import RegionSelector from './RegionSelector'
import FRASelector from './FRASelector'
import '../../assets/Profile.scss'

function RequestAccessForm({
  user,
  sttList,
  editMode = false,
  initialValues = {},
  onCancel,
}) {
  const errorRef = useRef(null)

  const isAMSUser = user?.email?.includes('@acf.hhs.gov')
  const primaryRole = user?.roles?.[0]

  const [errors, setErrors] = useState({})
  const [profileInfo, setProfileInfo] = useState({
    firstName: initialValues.firstName || '',
    lastName: initialValues.lastName || '',
    stt: initialValues.stt || '',
    hasFRAAccess: initialValues.hasFRAAccess ?? (isAMSUser ? false : null),
    regions: initialValues.regions || new Set(),
  })
  const [originalData] = useState(profileInfo) // This should be done when editing begins

  const dispatch = useDispatch()
  const [touched, setTouched] = useState({})
  const displayingError =
    !!Object.keys(errors).length && !!Object.keys(touched).length

  const [jurisdictionType, setJurisdictionTypeInputValue] = useState(
    initialValues.jurisdictionType || 'state'
  )

  const regionError = 'At least one Region is required'

  const EditAccessFormRow = ({ label, value }) => (
    <div className="grid-row margin-bottom-1">
      <div className="grid-col-8 text-bold">{label}</div>
      <div className="grid-col text-no-wrap">{value}</div>
    </div>
  )

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

  const getJurisdictionLocationInfo = () => {
    if (jurisdictionType === 'state') {
      return <EditAccessFormRow label="State" value={profileInfo.stt} />
    } else if (jurisdictionType === 'territory') {
      return <EditAccessFormRow label="Territory" value={profileInfo.stt} />
    } else {
      return <EditAccessFormRow label="Tribe" value={profileInfo.stt} />
    }
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
            displayingError || errors.form ? 'display-block' : 'display-none'
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
          <>
            {isAMSUser ? (
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
            ) : (
              <>
                <div className="grid-row">
                  <div className="grid-col-8">
                    <hr className="margin-top-3 margin-bottom-3 full-width-hr" />
                  </div>
                </div>
                <EditAccessFormRow
                  label="User Type"
                  value={primaryRole?.name}
                />
                <EditAccessFormRow
                  label="Jurisdiction Type"
                  value={
                    jurisdictionType.charAt(0).toUpperCase() +
                    jurisdictionType.slice(1)
                  }
                />
                {getJurisdictionLocationInfo()}
                <div className="grid-row">
                  <div className="grid-col-8">
                    <hr className="margin-bottom-1 margin-top-1 full-width-hr" />
                  </div>
                </div>
              </>
            )}
          </>
        ) : (
          <>
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
          </>
        )}
        {jurisdictionType !== 'tribe' && !isAMSUser && (
          <FRASelector
            hasFRAAccess={profileInfo.hasFRAAccess}
            setHasFRAAccess={setHasFRAAccess}
            error={errors.hasFRAAccess}
          />
        )}
        <div className="usa-button-group">
          <Button type="submit" className="width-full request-access-button">
            {editMode ? 'Save Changes' : 'Request Access'}
          </Button>
          {editMode && (
            <Button
              type="button"
              className="margin-top-2"
              outline
              onClick={onCancel}
            >
              Cancel
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}

export default RequestAccessForm
