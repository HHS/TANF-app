import React from 'react'
import { useSelector } from 'react-redux'
import ProfileRow from './ProfileRow'
import JurisdictionLocationInfo from './JurisdictionLocationInfo'
import { getRegionNameById } from '../../utils/regions'
import { accountStatusIsApproved } from '../../selectors/auth'

const UserProfileDetails = ({ user, isAMSUser, hasFRAAccess = false }) => {
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)

  const userJurisdiction = user?.stt?.type || 'state'
  const userLocationName = user?.stt?.name || 'Federal Government'
  const userRegions = user?.regions ?? []

  const hasRegions = Array.isArray(userRegions) && userRegions.length > 0

  return (
    <div data-testid="user-profile-info">
      <ProfileRow
        label="Name"
        value={`${user?.first_name || ''} ${user?.last_name || ''}`}
      />
      <hr className="margin-right-8 margin-top-2 margin-bottom-2" />
      {isAMSUser ? (
        hasRegions ? (
          <>
            <ProfileRow
              label="Regional Office(s)"
              value={
                <>
                  {userRegions.map((region, index) => (
                    <div key={index}>
                      {`Region ${region.id} (${getRegionNameById(region.id)})`}
                    </div>
                  ))}
                </>
              }
            />
            <hr className="margin-right-8 margin-top-3 margin-bottom-2" />
          </>
        ) : (
          !userAccessRequestApproved && (
            <>
              <ProfileRow label="Regional Office(s)" value="None selected" />
              <hr className="margin-right-8 margin-top-3 margin-bottom-2" />
            </>
          )
        )
      ) : (
        <>
          <ProfileRow
            label="Jurisdiction Type"
            value={
              userJurisdiction.charAt(0).toUpperCase() +
              userJurisdiction.slice(1)
            }
          />
          <JurisdictionLocationInfo
            jurisdictionType={userJurisdiction}
            locationName={userLocationName}
            formType={'profile'}
          />
          {userJurisdiction !== 'tribe' && !isAMSUser && (
            <ProfileRow
              label="Reporting FRA"
              value={hasFRAAccess ? 'Yes' : 'No'}
            />
          )}
        </>
      )}
    </div>
  )
}

export default UserProfileDetails
