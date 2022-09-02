import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

import loginLogo from '../../assets/login-gov-logo.svg'
import Button from '../Button'

function Profile() {
  const user = useSelector((state) => state.auth.user)
  const hasRoles = user?.roles.length > 0
  // Most higher-env users will only have a single role, so just grab the first one.
  const primaryRole = user?.roles[0]
  const missingAccessRequest = !Boolean(user?.access_request)
  const isAccessRequestPending = Boolean(user?.access_request) && !hasRoles

  const isAMSUser = user?.email?.includes('@acf.hhs.gov')

  if (missingAccessRequest) {
    return <Navigate to="/home" />
  }

  return (
    <div className="usa-prose">
      {isAccessRequestPending && (
        <div className="usa-alert usa-alert--info margin-top-3">
          <div className="usa-alert__body">
            <p className="usa-alert__text" id="page-alert">
              Your request for access is currently being reviewed by an OFA
              Admin. We’ll send you an email when it’s been approved.
            </p>
          </div>
        </div>
      )}
      <div>
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
      </div>
      <div className="margin-top-5">
        <p className="text-bold">Email and Password</p>

        {isAMSUser ? (
          <p>
            You will receive all communications from the TANF Data Portal via
            your ACF email address.
          </p>
        ) : (
          <>
            <p>
              You will receive all communications from the TANF Data Portal via
              the email address you registered with Login.gov. Your email or
              password can be managed via Login.gov
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
              <span className="visually-hidden">Opens in a new website</span>
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

export default Profile
