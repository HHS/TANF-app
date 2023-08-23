import React, { useRef, useState } from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useDispatch, useSelector } from 'react-redux'
import signOut from '../../utils/signOut'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'
import ResourceCards from '../ResourceCards'
import {
  accountStatusIsApproved,
  accountIsInReview,
  selectPrimaryUserRole,
} from '../../selectors/auth'

/**
 * Home renders the Request Access form for creating a profile, and displays
 * a pending-approval state, before showing the user their active roles and
 * permissions once they are approved by an Admin in the backend.
 */
function Home() {
  const errorRef = useRef(null)

  const user = useSelector((state) => state.auth.user)
  const role = useSelector(selectPrimaryUserRole)

  const [errors, setErrors] = useState({})
  const [profileInfo, setProfileInfo] = useState({
    firstName: '',
    lastName: '',
    stt: '',
  })
  const dispatch = useDispatch()
  const [touched, setTouched] = useState({})

  const sttList = useSelector((state) => state?.stts?.sttList)

  const userAccessInReview = useSelector(accountIsInReview)
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)

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

  if (userAccessInReview) {
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
  } else if (!userAccessRequestApproved) {
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

  return (
    <>
      <div className="margin-top-5">
        <p className="margin-top-1 margin-bottom-4">
          You have been approved for access to TDP. For guidance on submitting
          data, managing your account, and utilizing other functionality please
          refer to the TDP Knowledge Center.
        </p>
        <table className="usa-table usa-table--striped">
          <caption>
            <b> Data Reporting Deadlines </b>
          </caption>
          <thead>
            <tr>
              <th scope="col">Fiscal Quarter</th>
              <th scope="col">Calendar Period</th>
              <th scope="col">Due Date</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>Oct 1 - Dec 31</td>
              <td>February 14</td>
            </tr>
            <tr>
              <td>2</td>
              <td>Jan 1 - Mar 31</td>
              <td>May 15</td>
            </tr>
            <tr>
              <td>3</td>
              <td>Apr 1 - Jun 30</td>
              <td>August 14</td>
            </tr>
            <tr>
              <td>4</td>
              <td>Jul 1 - Sep 30</td>
              <td>November 14</td>
            </tr>
          </tbody>
        </table>
      </div>
      <br />
      <hr />
      <br />
      <ResourceCards />
    </>
  )
}

export default Home
