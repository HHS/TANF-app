import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

import loginLogo from '../../assets/login-gov-logo.svg'
import Button from '../Button'
import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import {
  accountIsInReview,
  accountIsMissingAccessRequest,
} from '../../selectors/auth'

function Profile({ isEditing, onEdit, onCancel }) {
  const user = useSelector((state) => state.auth.user)
  // Most higher-env users will only have a single role, so just grab the first one.
  const primaryRole = user?.roles?.[0]
  const missingAccessRequest = useSelector(accountIsMissingAccessRequest)
  const isAccessRequestPending = useSelector(accountIsInReview) // TODO: make this true to see how this looks

  const isAMSUser = user?.email?.includes('@acf.hhs.gov')
  const userJurisdiction = user?.stt?.type || 'state'
  const userLocationName = user?.stt?.name || 'Federal Government'
  const userIsReportingFRA = user?.permissions?.includes('has_fra_access')
    ? 'Yes'
    : 'No'
  const userRegions = user?.regions

  if (missingAccessRequest) {
    return <Navigate to="/home" />
  }

  if (isEditing) {
    return (
      <RequestAccessForm
        user={user}
        editMode={true}
        onCancel={onCancel}
        initialValues={{
          firstName: user?.first_name || '',
          lastName: user?.last_name || '',
          stt: user?.stt?.name || '',
          hasFRAAccess: user?.permissions?.includes('has_fra_access') ?? null,
          regions: new Set(user?.regions || []),
          jurisdictionType: user?.stt?.type || 'state',
        }}
      />
    )
  }

  const ProfileRow = ({ label, value }) => (
    <div className="grid-row margin-bottom-1">
      <div className="grid-col-2 text-bold">{label}</div>
      <div className="grid-col">{value}</div>
    </div>
  )

  const getJurisdictionLocationInfo = () => {
    if (userJurisdiction === 'state') {
      return <ProfileRow label="State" value={userLocationName} />
    } else if (userJurisdiction === 'territory') {
      return <ProfileRow label="Territory" value={userLocationName} />
    } else {
      return <ProfileRow label="Tribe" value={userLocationName} />
    }
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
      <div data-testid="user-profile" className="margin-top-4 margin-bottom-3">
        <div data-testid="user-profile-container">
          <div data-testid="user-profile-info">
            <ProfileRow
              label="Name"
              value={`${user?.first_name || ''} ${user?.last_name || ''}`}
            />
            <hr className="margin-right-4 margin-top-3" />
            <ProfileRow label="User Type" value={primaryRole?.name} />
            {isAMSUser ||
            (userLocationName !== 'Federal Governement' &&
              userRegions.length !== 0) ? (
              <ProfileRow label="Regional Office(s)" value={userRegions} />
            ) : (
              <>
                <ProfileRow
                  label="Jurisdiction Type"
                  value={
                    userJurisdiction.charAt(0).toUpperCase() +
                      userJurisdiction.slice(1) || 'State'
                  }
                />
                {getJurisdictionLocationInfo()}
                {userJurisdiction !== 'tribe' && !isAMSUser && (
                  <ProfileRow
                    label="Reporting FRA"
                    value={userIsReportingFRA}
                  />
                )}
              </>
            )}
            <hr className="margin-right-4 margin-top-3" />
          </div>
        </div>
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
