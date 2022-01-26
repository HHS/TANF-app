import React, { useEffect, useRef, useState } from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useDispatch, useSelector } from 'react-redux'
import signOut from '../../utils/signOut'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'
import { validation } from '../Profile/Profile'
import { useEventLogger } from '../../utils/eventLogger'
import { setAlert } from '../../actions/alert'
import { ALERT_ERROR } from '../Alert'
import { Redirect } from 'react-router-dom'

function Home() {
  const errorRef = useRef(null)
  const sttAssigned = useSelector((state) => state.auth.user.stt)

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

  const logger = useEventLogger()
  const sttList = useSelector((state) => state.stts.sttList)

  const userAccessRequestApproved = Boolean(user?.['access_request'])

  const requestAccessError = useSelector((state) => state.requestAccess.error)

  useEffect(() => {
    if (requestAccessError) {
      dispatch(
        setAlert({ heading: requestAccessError.message, type: ALERT_ERROR })
      )
      logger.error(requestAccessError.message)
    }
  }, [dispatch, requestAccessError, logger])

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

  if (userAccessRequestApproved && sttAssigned) {
    return <Redirect to="/home" />
  }

  return (
    <div className="margin-top-5">
      {!hasRole ? (
        <>
          <div className="margin-top-5">
            <p className="margin-top-1 margin-bottom-4">
              Your request for access is currently being reviewed by an OFA
              Admin. We'll send you an email when it's been approved.
            </p>
          </div>
        </>
      ) : (
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
              <STTComboBox
                selectStt={setStt}
                error={Boolean(errors.stt)}
                selectedStt={profileInfo?.stt}
                handleBlur={handleBlur}
              />
            </div>
            <Button type="submit" className="width-full request-access-button">
              Request Access
            </Button>
          </form>
        </>
      )}
      <Button
        type="button"
        className="width-tablet margin-bottom-4"
        onClick={signOut}
      >
        <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
        Sign Out
      </Button>
    </div>
  )
}

export default Home
