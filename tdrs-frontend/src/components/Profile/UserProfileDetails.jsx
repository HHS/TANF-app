import React from 'react'
import { useSelector } from 'react-redux'
import ProfileRow from './ProfileRow'
import JurisdictionLocationInfo from './JurisdictionLocationInfo'
import { getRegionNameById } from '../../utils/regions'
import { FORM_TYPES } from '../../utils/formHelpers'
import { accountStatusIsApproved } from '../../selectors/auth'

const UserProfileDetails = ({
  user,
  isAMSUser,
  hasFRAAccess = false,
  pendingChangeRequests = [],
}) => {
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)

  const userJurisdiction = user?.stt?.type || 'state'
  const userLocationName = user?.stt?.name || 'Federal Government'
  const userRegions = user?.regions ?? []

  const hasRegions = Array.isArray(userRegions) && userRegions.length > 0
  const pendingChangesByField = Array.isArray(pendingChangeRequests)
    ? pendingChangeRequests.reduce((acc, request) => {
        if (
          !request?.field_name ||
          request?.status !== 'pending' ||
          acc[request.field_name]
        ) {
          return acc
        }
        acc[request.field_name] = request.requested_value
        return acc
      }, {})
    : {}

  const pendingFirstName = pendingChangesByField.first_name
  const pendingLastName = pendingChangesByField.last_name
  const pendingNameDisplay =
    pendingFirstName || pendingLastName
      ? `${pendingFirstName ?? ''} ${pendingLastName ?? ''}`.trim()
      : null

  const parseRegionIds = (value) => {
    if (!value) {
      return []
    }
    if (Array.isArray(value)) {
      return value
        .map((entry) => Number(entry))
        .filter((entry) => Number.isFinite(entry))
    }
    if (typeof value !== 'string') {
      return []
    }
    const cleaned = value.replace(/[\[\]\s'"]/g, '')
    if (!cleaned) {
      return []
    }
    return cleaned
      .split(',')
      .map((entry) => Number(entry))
      .filter((entry) => Number.isFinite(entry))
  }

  const pendingRegionIds = parseRegionIds(pendingChangesByField.regions)
  const pendingRegionsDisplay =
    pendingRegionIds.length > 0 ? (
      <>
        {pendingRegionIds.map((regionId) => (
          <div key={regionId}>
            {`Region ${regionId} (${getRegionNameById(regionId)})`}
          </div>
        ))}
      </>
    ) : null

  const formatPendingFRAAccess = (value) => {
    if (typeof value === 'boolean') {
      return value ? 'Yes' : 'No'
    }
    if (typeof value === 'string') {
      const normalized = value.toLowerCase()
      if (normalized === 'true') {
        return 'Yes'
      }
      if (normalized === 'false') {
        return 'No'
      }
    }
    return value
  }

  const pendingFRAAccess = formatPendingFRAAccess(
    pendingChangesByField.has_fra_access
  )

  const shouldShowRegionsRow =
    hasRegions || Boolean(pendingRegionsDisplay) || !userAccessRequestApproved

  return (
    <div data-testid="user-profile-info">
      <ProfileRow
        label="Name"
        value={`${user?.first_name || ''} ${user?.last_name || ''}`}
        requestedValue={pendingNameDisplay}
      />
      <hr className="margin-right-8 margin-top-2 margin-bottom-2" />
      {isAMSUser ? (
        shouldShowRegionsRow && (
          <>
            <ProfileRow
              label="Regional Office(s)"
              value={
                hasRegions ? (
                  <>
                    {userRegions.map((region, index) => (
                      <div key={index}>
                        {`Region ${region.id} (${getRegionNameById(region.id)})`}
                      </div>
                    ))}
                  </>
                ) : (
                  'None selected'
                )
              }
              requestedValue={pendingRegionsDisplay}
            />
            <hr className="margin-right-8 margin-top-3 margin-bottom-2" />
          </>
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
            formType={FORM_TYPES.PROFILE}
          />
          {userJurisdiction !== 'tribe' && !isAMSUser && (
            <ProfileRow
              label="Reporting FRA"
              value={hasFRAAccess ? 'Yes' : 'No'}
              requestedValue={pendingFRAAccess}
            />
          )}
        </>
      )}
    </div>
  )
}

export default UserProfileDetails
