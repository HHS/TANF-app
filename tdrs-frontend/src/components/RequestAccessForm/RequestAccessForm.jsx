import React, { useRef, useState } from 'react'
import Button from '../Button'
import { useDispatch } from 'react-redux'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import ReadOnlyRow from './ReadOnlyRow'
import { requestAccess } from '../../actions/requestAccess'
import { updateUserRequest } from '../../actions/mockUpdateUserRequest'
import { getInitialProfileInfo, clearFormError } from '../../utils/formHelpers'
import JurisdictionSelector from './JurisdictionSelector'
import JurisdictionLocationInfo from '../Profile/JurisdictionLocationInfo'
import RegionSelector from './RegionSelector'
import FRASelector from './FRASelector'
import '../../assets/Profile.scss'

function RequestAccessForm({
  user,
  sttList,
  editMode = false,
  initialValues = {},
  onCancel,
  type = 'access request',
}) {
  const errorRef = useRef(null)
  const isAMSUser = user?.email?.includes('@acf.hhs.gov')
  const originallyHadFRAAccess = initialValues.hasFRAAccess ?? null

  const [profileInfo, setProfileInfo] = useState(
    getInitialProfileInfo(
      initialValues,
      isAMSUser,
      editMode,
      originallyHadFRAAccess
    )
  )
  const [originalData] = useState(profileInfo)
  const [errors, setErrors] = useState({})
  const [touched, setTouched] = useState({})
  const [jurisdictionType, setJurisdictionTypeInputValue] = useState(
    initialValues.jurisdictionType || 'state'
  )
  const [regional, setRegional] = useState(
    profileInfo?.regions instanceof Set && profileInfo.regions.size > 0
  )
  const [originalRegional] = useState(
    profileInfo?.regions instanceof Set && profileInfo.regions.size > 0
  )

  const dispatch = useDispatch()
  const fieldErrorKeys = Object.keys(errors).filter((key) => key !== 'form')
  const hasFieldErrors =
    fieldErrorKeys.length > 0 && Object.keys(touched).length > 0

  const showErrorSummary = hasFieldErrors || !!errors.form

  const regionError = 'At least one Region is required'
  const validateRegions = (regions) => {
    if (regions?.size === 0) {
      return regionError
    }
    return null
  }

  const validation = (fieldName, fieldValue) => {
    if (editMode) {
      if (fieldName === 'stt') {
        return null
      }

      if (
        fieldName === 'hasFRAAccess' &&
        (isAMSUser || jurisdictionType === 'tribe')
      ) {
        return null
      }
    }

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
    } else if (!isAMSUser) {
      setHasFRAAccess(true)
    } else {
      setHasFRAAccess(null) // AMS users shouldn't be setting FRA access
    }
  }

  const setStt = (sttName) => {
    setProfileInfo((currentState) => ({
      ...currentState,
      stt: sttName,
    }))
  }

  const setHasFRAAccess = (hasFRAAccess) => {
    if (errors.form) {
      setErrors(clearFormError(errors))
    }

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
      setErrors(clearFormError(errors))
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
      const hasChanges = () => {
        const profileChanged = Object.keys(profileInfo).some((key) => {
          if (key === 'regions') {
            const newRegions = Array.from(profileInfo[key])
              .map((r) => r.id)
              .sort()
            const originalRegions = Array.from(originalData[key])
              .map((r) => r.id)
              .sort()
            return (
              JSON.stringify(newRegions) !== JSON.stringify(originalRegions)
            )
          }

          if (typeof profileInfo[key] === 'object') {
            return (
              JSON.stringify(profileInfo[key]) !==
              JSON.stringify(originalData[key])
            )
          }
          return profileInfo[key] !== originalData[key]
        })

        const regionalChanged = regional !== originalRegional
        return profileChanged || regionalChanged
      }

      if (!hasChanges()) {
        setErrors({ form: 'No changes have been made.' })
        setTimeout(() => errorRef.current?.focus(), 0)
        return
      }
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
    const regionError =
      isAMSUser && regional ? validateRegions(profileInfo.regions) : null

    const combinedErrors = {
      ...formValidation.errors,
      ...(regionError && { regions: regionError }),
    }
    const combinedTouched = {
      ...formValidation.touched,
      ...(regionError && isAMSUser && { regions: true }),
    }

    setErrors(combinedErrors)
    setTouched(combinedTouched)

    if (!Object.values(combinedErrors).length) {
      const sttObj = sttList.find((stt) => stt.name === profileInfo.stt)
      const payload = {
        ...profileInfo,
        stt: sttObj,
        regions: Array.from(profileInfo.regions).map((region) => region.id),
      }

      if (editMode) {
        if (type === 'access request') {
          // PATCH call for updating Access Request
          return dispatch(requestAccess(payload)).then(() => {
            onCancel() // toggles editMode to false after update
          })
        }
        // TODO: update with real API call (need to rename mock function name to reflect profile)
        // Simulate profile update
        return dispatch(updateUserRequest(payload)).then(() => {
          onCancel() // toggles editMode to false after update
        })
      } else {
        // Submit new access request
        return dispatch(requestAccess(payload))
      }
    }

    return setTimeout(() => errorRef.current.focus(), 0)
  }

  const regionSelectorProps = {
    setErrors,
    errors,
    setTouched,
    touched,
    setProfileInfo,
    profileInfo,
    displayingError: hasFieldErrors,
    validateRegions,
    regionError,
    regional,
    setRegional,
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
        {editMode && !isAMSUser && (
          <div>
            <hr className="form-section-divider" />
            <ReadOnlyRow
              label="Jurisdiction Type"
              value={
                (jurisdictionType?.charAt(0)?.toUpperCase() ?? '') +
                (jurisdictionType?.slice(1) ?? '')
              }
            />
            <JurisdictionLocationInfo
              jurisdictionType={jurisdictionType}
              locationName={profileInfo.stt || 'Federal Government'}
              formType={'access request'}
            />
            <hr className="form-section-divider" />
          </div>
        )}

        {!editMode && !isAMSUser && (
          <>
            <JurisdictionSelector setJurisdictionType={setJurisdictionType} />
            {jurisdictionType && (
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
          </>
        )}

        {jurisdictionType !== 'tribe' && !isAMSUser && (
          <FRASelector
            hasFRAAccess={profileInfo.hasFRAAccess}
            setHasFRAAccess={setHasFRAAccess}
            error={errors.hasFRAAccess}
          />
        )}

        {isAMSUser && <RegionSelector {...regionSelectorProps} />}

        {!editMode ? (
          <Button type="submit" className="width-full request-access-button">
            Request Access
          </Button>
        ) : (
          <div className="usa-button-group margin-top-3">
            <button
              type="submit"
              className="usa-button"
              style={{ minWidth: '300px' }}
            >
              {type === 'profile' ? 'Save Changes' : 'Update Request'}
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
