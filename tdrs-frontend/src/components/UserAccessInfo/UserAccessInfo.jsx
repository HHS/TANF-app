import React from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useSelector } from 'react-redux'
import signOut from '../../utils/signOut'

const UserAccessInfo = ({ onEditClick }) => {
  const user = useSelector((state) => state.auth.user)
  const primaryRole = user?.roles?.[0]

  const userState = user?.stt?.name || 'Federal Government'
  const userJurisdiction = user?.stt?.type || 'State'
  const userIsReportingFRA = user?.has_fra_access ? 'Yes' : 'No'

  const ProfileRow = ({ label, value }) => (
    <div className="grid-row margin-bottom-1">
      <div className="grid-col-2 text-bold">{label}</div>
      <div className="grid-col">{value}</div>
    </div>
  )

  return (
    <div data-testid="user-access-request-profile" className="usa-prose">
      <div data-testid="user-access-profile-container">
        <div data-testid="user-access-info">
          <ProfileRow
            label="Name"
            value={`${user?.first_name || ''} ${user?.last_name || ''}`}
          />
          <hr className="margin-right-4" />
          <ProfileRow label="User Type" value={primaryRole?.name} />
          <ProfileRow
            label="Jurisdiction Type"
            value={
              userJurisdiction.charAt(0).toUpperCase() +
                userJurisdiction.slice(1) || 'State'
            }
          />
          <ProfileRow label="State" value={userState} />
          <ProfileRow label="Reporting FRA" value={userIsReportingFRA} />
        </div>
        <div className="margin-top-9">
          <div className="usa-button-group margin-top-4 margin-bottom-4">
            <button
              type="button"
              className="usa-button margin-right-3"
              style={{ minWidth: '350px' }}
              onClick={onEditClick}
            >
              Edit Profile Information
            </button>
            <Button type="button" className="usa-button" onClick={signOut}>
              <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default UserAccessInfo
