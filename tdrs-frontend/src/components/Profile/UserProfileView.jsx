// src/components/UserProfileView.jsx
import React from 'react'
import Button from '../Button'
import ProfileRow from './ProfileRow'
import UserProfileDetails from './UserProfileDetails'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import loginLogo from '../../assets/login-gov-logo.svg'
import signOut from '../../utils/signOut'

const UserProfileView = ({
  user,
  isAMSUser,
  isAccessRequestPending,
  onEdit,
  type = 'profile',
  hasFRAAccess = false,
}) => {
  // Sections for the user profile view (readability)
  const EditProfileButton = ({ onEdit }) => (
    <div className="margin-top-3">
      <div className="margin-top-2 margin-bottom-2">
        <button
          type="button"
          className="usa-button"
          style={{ minWidth: '350px' }}
          onClick={onEdit}
        >
          Edit Profile Information
        </button>
        <p style={{ fontStyle: 'italic' }}>
          * Any changes submitted will be reviewed by an OFA admin.
        </p>
      </div>
    </div>
  )

  const EditAccessRequestButtons = ({ onEdit, signOut }) => (
    <div className="margin-top-10">
      <div className="usa-button-group margin-top-4 margin-bottom-4">
        <button
          type="button"
          className="usa-button margin-right-3"
          style={{ minWidth: '350px' }}
          onClick={onEdit}
        >
          Edit Access Request
        </button>
        <Button type="button" className="usa-button" onClick={signOut}>
          <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
          Sign Out
        </Button>
      </div>
    </div>
  )

  const AMSUserEmail = ({ email }) => (
    <>
      <p>
        You will receive all communications from the TANF Data Portal via your
        ACF email address.
      </p>
      <div className="margin-top-2 margin-bottom-4">
        <ProfileRow label="Email" value={email} />
      </div>
    </>
  )

  const LoginGovEmail = ({ email }) => (
    <>
      <p>
        You will receive all communications from the TANF Data Portal via the
        email address you registered with Login.gov. <br />
        Your email or password can be managed via Login.gov
      </p>
      <div className="margin-top-2 margin-bottom-2">
        <ProfileRow label="Email" value={email} />
      </div>
      <Button
        className="sign-in-button margin-bottom-3"
        type="button"
        id="loginDotGovSignIn"
        target="_self"
        href={`${process.env.REACT_APP_LOGIN_GOV_URL}`}
      >
        <div className="mobile:margin-x-auto mobile-lg:margin-0">
          Manage Your Account at{' '}
          <img
            className="mobile:margin-x-auto mobile:padding-top-1 mobile-lg:margin-0 mobile-lg:padding-top-0 width-15 padding-left-1"
            src={loginLogo}
            alt="Login.gov"
          />
        </div>
        <span className="visually-hidden">Opens in a new website</span>
      </Button>
    </>
  )

  return (
    <div className="usa-prose">
      {isAccessRequestPending && (
        <div>
          <div className="usa-alert usa-alert--info margin-top-3 margin-right-8">
            <div className="usa-alert__body" role="alert">
              <p className="usa-alert__text" id="page-alert">
                Your request for access is currently being reviewed by an OFA
                Admin. We’ll send you an email when it’s been approved.
              </p>
            </div>
          </div>
        </div>
      )}

      <div data-testid="user-profile" className="margin-top-5 margin-bottom-3">
        <div data-testid="user-profile-container">
          <div className="margin-top-4 margin-bottom-3">
            <UserProfileDetails
              user={user}
              isAMSUser={isAMSUser}
              hasFRAAccess={hasFRAAccess}
            />
          </div>
        </div>
      </div>
      {type === 'profile' ? (
        <>
          <EditProfileButton onEdit={onEdit} />

          <div className="margin-top-5">
            <p className="text-bold">Email and Password</p>
            {isAMSUser ? (
              <AMSUserEmail email={user?.email} />
            ) : (
              <LoginGovEmail email={user?.email} />
            )}
          </div>
        </>
      ) : (
        <EditAccessRequestButtons onEdit={onEdit} signOut={signOut} />
      )}
    </div>
  )
}

export default UserProfileView
