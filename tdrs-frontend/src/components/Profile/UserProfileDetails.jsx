import React from 'react'
import ProfileRow from './ProfileRow'
import JurisdictionLocationInfo from './JurisdictionLocationInfo'

const UserProfileDetails = ({ user, isAMSUser }) => {
  // Most higher-env users will only have a single role, so just grab the first one.
  const primaryRole = user?.roles?.[0]
  const userJurisdiction = user?.stt?.type || 'state'
  const userLocationName = user?.stt?.name || 'Federal Government'
  const userRegions = user?.regions
  const userIsReportingFRA = user?.permissions?.includes('has_fra_access')
    ? 'Yes'
    : 'No'

  return (
    <div data-testid="user-profile-info">
      <ProfileRow
        label="Name"
        value={`${user?.first_name || ''} ${user?.last_name || ''}`}
      />
      <hr className="margin-right-8 margin-top-3 margin-bottom-2" />
      <ProfileRow label="User Type" value={primaryRole?.name} />
      {isAMSUser && userRegions ? (
        <ProfileRow
          label="Regional Office(s)"
          value={
            <>
              {userRegions.map((region, index) => (
                <div key={index}>{`Region ${region.id} (${region.name})`}</div>
              ))}
            </>
          }
        />
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
            <ProfileRow label="Reporting FRA" value={userIsReportingFRA} />
          )}
        </>
      )}
    </div>
  )
}

export default UserProfileDetails
