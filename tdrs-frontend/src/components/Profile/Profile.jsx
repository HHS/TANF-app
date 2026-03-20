import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'

import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import UserProfileView from './UserProfileView'
import { get } from '../../fetch-instance'
import { getRegionNameById } from '../../utils/regions'
import {
  accountHasPendingProfileChange,
  accountIsInReview,
  accountIsMissingAccessRequest,
  selectUser,
} from '../../selectors/auth'
import { JURISDICTION_TYPES } from './JurisdictionLocationInfo'

function Profile({
  isEditing = false,
  onEdit,
  type,
  user,
  sttList = [],
  onCancel,
  setInEditMode,
}) {
  const authUser = useSelector(selectUser)
  const resolvedUser = user ?? authUser
  const isAMSUser = resolvedUser?.email?.includes('@acf.hhs.gov')
  const userPermissions =
    resolvedUser?.permissions?.map((p) => p.codename) || []
  const hasFRAAccess = userPermissions.includes('has_fra_access')
  const userId = resolvedUser?.id
  const pendingRequestCount = resolvedUser?.pending_requests ?? 0

  const missingAccessRequest = useSelector(accountIsMissingAccessRequest)
  const isAccessRequestPending = useSelector(accountIsInReview)
  const isProfileChangePending = useSelector(accountHasPendingProfileChange)
  const [pendingChangeRequests, setPendingChangeRequests] = useState([])
  const [pendingChangeRequestsLoaded, setPendingChangeRequestsLoaded] =
    useState(false)
  const pendingChangesByField = Array.isArray(pendingChangeRequests)
    ? pendingChangeRequests.reduce((acc, request) => {
        if (
          !request?.field_name ||
          request?.status !== 'pending' ||
          acc[request.field_name] !== undefined
        ) {
          return acc
        }
        acc[request.field_name] = request.requested_value
        return acc
      }, {})
    : {}

  const resolvePendingFRAAccess = (value) => {
    if (typeof value === 'boolean') {
      return value
    }
    if (typeof value === 'string') {
      const normalized = value.toLowerCase()
      if (normalized === 'true') {
        return true
      }
      if (normalized === 'false') {
        return false
      }
    }
    return null
  }

  const parsePendingRegionIds = (value) => {
    if (value === null || typeof value === 'undefined') {
      return []
    }

    if (Array.isArray(value)) {
      return value
        .map((entry) => {
          if (entry && typeof entry === 'object') {
            return Number(entry.id)
          }
          return Number(entry)
        })
        .filter((entry) => Number.isFinite(entry))
    }

    if (typeof value === 'number') {
      return Number.isFinite(value) ? [value] : []
    }

    if (typeof value !== 'string') {
      return []
    }

    try {
      const parsedValue = JSON.parse(value)
      return parsePendingRegionIds(parsedValue)
    } catch {
      const cleaned = value.replace(/[\[\]\s'"]/g, '')
      if (!cleaned) {
        return []
      }
      return cleaned
        .split(',')
        .map((entry) => Number(entry))
        .filter((entry) => Number.isFinite(entry))
    }
  }

  const pendingRegionIds = parsePendingRegionIds(pendingChangesByField.regions)
  const pendingRegions =
    pendingRegionIds.length > 0
      ? pendingRegionIds.map((regionId) => ({
          id: regionId,
          name: getRegionNameById(regionId),
        }))
      : null

  useEffect(() => {
    if (setInEditMode) {
      setInEditMode(isEditing, type)
    }
  }, [isEditing, type, setInEditMode])

  useEffect(() => {
    let isMounted = true

    const loadPendingChangeRequests = async () => {
      if (!userId || type !== 'profile' || pendingRequestCount === 0) {
        if (isMounted) {
          setPendingChangeRequests([])
          setPendingChangeRequestsLoaded(true)
        }
        return
      }

      try {
        if (isMounted) {
          setPendingChangeRequestsLoaded(false)
        }
        const response = await get(
          `${process.env.REACT_APP_BACKEND_URL}/change-requests/`,
          { withCredentials: true }
        )
        if (!response?.ok) {
          throw response?.error || new Error('Failed to load change requests')
        }
        const data = response?.data?.results ?? response?.data ?? []
        const pendingRequests = Array.isArray(data)
          ? data.filter(
              (request) =>
                request?.user === userId && request?.status === 'pending'
            )
          : []
        if (isMounted) {
          setPendingChangeRequests(pendingRequests)
          setPendingChangeRequestsLoaded(true)
        }
      } catch (error) {
        if (isMounted) {
          setPendingChangeRequests([])
          setPendingChangeRequestsLoaded(true)
        }
      }
    }

    loadPendingChangeRequests()

    return () => {
      isMounted = false
    }
  }, [userId, type, pendingRequestCount])

  if (isEditing) {
    if (
      type === 'profile' &&
      pendingRequestCount > 0 &&
      !pendingChangeRequestsLoaded
    ) {
      return null
    }

    return (
      <RequestAccessForm
        user={resolvedUser}
        sttList={sttList}
        editMode={isEditing}
        initialValues={{
          firstName:
            pendingChangesByField.first_name ?? resolvedUser?.first_name ?? '',
          lastName:
            pendingChangesByField.last_name ?? resolvedUser?.last_name ?? '',
          stt: resolvedUser?.stt?.name || '',
          hasFRAAccess:
            resolvePendingFRAAccess(pendingChangesByField.has_fra_access) ??
            hasFRAAccess ??
            null,
          regions: pendingRegions ?? resolvedUser?.regions ?? new Set(),
          jurisdictionType: resolvedUser?.stt?.type || JURISDICTION_TYPES.STATE,
        }}
        onCancel={onCancel}
        type={type}
      />
    )
  }

  if (missingAccessRequest) {
    return <RequestAccessForm user={resolvedUser} sttList={sttList} />
  }

  return (
    <UserProfileView
      user={resolvedUser}
      isAMSUser={isAMSUser}
      isAccessRequestPending={isAccessRequestPending}
      isProfileChangePending={isProfileChangePending}
      pendingChangeRequests={pendingChangeRequests}
      onEdit={onEdit}
      type={type}
      hasFRAAccess={hasFRAAccess ?? null}
    />
  )
}

export default Profile
