// src/components/UserProfileView.jsx
import React from 'react'
import Button from '../Button'
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
}) => {
  return (
    <div className="usa-prose">
      {isAccessRequestPending && (
        <div className="margin-top-5">
          <div className="usa-alert usa-alert--slim usa-alert--info margin-top-3">
            <div className="usa-alert__body" role="alert">
              <p className="usa-alert__text" id="page-alert">
                Your request for access is currently being reviewed by an OFA
                Admin. We’ll send you an email when it’s been approved.
              </p>
            </div>
          </div>
        </div>
      )}

      <div data-testid="user-profile" className="margin-top-4 margin-bottom-3">
        <div data-testid="user-profile-container">
          <div className="margin-top-4 margin-bottom-3">
            <UserProfileDetails user={user} isAMSUser={isAMSUser} />
          </div>
        </div>
        {type === 'profile' && <hr className="margin-right-4 margin-top-3" />}
      </div>
      {/* <div data-testid="user-access-request-profile">
        <p id="full-name" className="text-bold">
          {user?.first_name} {user?.last_name}
        </p>
        <p>{user?.email}</p>
        <p>{primaryRole?.name}</p>
        {(() => {
          const stt = user?.stt?.name || 'Federal Government'
         const region = user?.stt?.region || user?.region?.id

          if (stt === 'Federal Government' && !region) {
            return <p> {stt} </p>
          } else {
            return (
              <>
                <p> {stt} </p>
                <p> Region {region} </p>
              </>
            )
          }
        })()}
      </div> */}
      {type === 'profile' ? (
        <>
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
          <div className="margin-top-5">
            <p className="text-bold">Email and Password</p>
            {isAMSUser ? (
              <p>
                You will receive all communications from the TANF Data Portal
                via your ACF email address.
              </p>
            ) : (
              <>
                <p>
                  You will receive all communications from the TANF Data Portal
                  via the email address you registered with Login.gov. Your
                  email or password can be managed via Login.gov
                </p>
                <Button
                  className="sign-in-button"
                  type="button"
                  id="loginDotGovSignIn"
                  target={'_self'}
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
                  <span className="visually-hidden">
                    Opens in a new website
                  </span>
                </Button>
              </>
            )}
          </div>
        </>
      ) : (
        <div className="margin-top-9">
          <div className="usa-button-group margin-top-4 margin-bottom-4">
            <button
              type="button"
              className="usa-button margin-right-3"
              style={{ minWidth: '350px' }}
              onClick={onEdit}
            >
              Edit Profile Information
            </button>
            <Button type="button" className="usa-button" onClick={signOut}>
              <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
              Sign Out
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default UserProfileView
