import React, { useRef, useState } from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useDispatch, useSelector } from 'react-redux'
import signOut from '../../utils/signOut'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'

/**
 * Home renders the Request Access form for creating a profile, and displays
 * a pending-approval state, before showing the user their active roles and
 * permissions once they are approved by an Admin in the backend.
 */
function Home() {
  const errorRef = useRef(null)

  const user = useSelector((state) => state.auth.user)
  const role = user?.roles
  const hasRole = Boolean(role?.length > 0)
  const [errors, setErrors] = useState({})
  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })
  const dispatch = useDispatch()
  const [touched, setTouched] = useState({})

  const sttList = useSelector((state) => state?.stts?.sttList)

  const userAccessRequestApproved = Boolean(user?.['access_request'])

  const shouldShowSttComboBox = !user?.email?.includes('@acf.hhs.gov')

  const validation = (fieldName, fieldValue) => {
    const field = {
      firstName: 'First Name',
      lastName: 'Last Name',
      stt: shouldShowSttComboBox && 'A state, tribe, or territory',
    }[fieldName]

    if (
      Boolean(field) &&
      typeof fieldValue === 'string' &&
      fieldValue.trim() === ''
    ) {
      return `${field} is required`
    }
    return null
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

  if (!userAccessRequestApproved) {
    return (
      <div className="margin-top-5">
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
          {shouldShowSttComboBox && (
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
          )}
          <Button type="submit" className="width-full request-access-button">
            Request Access
          </Button>
        </form>
      </div>
    )
  }

  if (userAccessRequestApproved && !hasRole) {
    return (
      <div className="margin-top-5">
        <div className="margin-top-5">
          <p className="margin-top-1 margin-bottom-4" id="page-alert">
            Your request for access is currently being reviewed by an OFA Admin.
            We'll send you an email when it's been approved.
          </p>
        </div>
        <Button type="button" onClick={signOut}>
          <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
          Sign Out
        </Button>
      </div>
    )
  }

  return (
    <div className="margin-top-5">
      <p className="margin-top-1 margin-bottom-4">
        You've been approved as a(n) {role?.[0].name}. You'll be able to do the
        following in TDP:
      </p>
      <ul>
        {role?.[0]?.permissions?.map((permission) => (
          <li key={permission.id} id={permission.id}>
            {permission.name}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Home
