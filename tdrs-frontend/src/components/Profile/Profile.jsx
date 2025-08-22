import React, { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import UserProfileView from './UserProfileView'
import {
  accountIsInReview,
  accountIsMissingAccessRequest,
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
  const isAMSUser = user?.email?.includes('@acf.hhs.gov')
  const userPermissions = user?.permissions?.map((p) => p.codename) || []
  const hasFRAAccess = userPermissions.includes('has_fra_access')

  const missingAccessRequest = useSelector(accountIsMissingAccessRequest)
  const isAccessRequestPending = useSelector(accountIsInReview)

  useEffect(() => {
    if (setInEditMode) {
      setInEditMode(isEditing, type)
    }
  }, [isEditing, type, setInEditMode])

  if (missingAccessRequest) {
    return <Navigate to="/home" />
  }

  if (isEditing) {
    return (
      <RequestAccessForm
        user={user}
        sttList={sttList}
        editMode={isEditing}
        initialValues={{
          firstName: user?.first_name || '',
          lastName: user?.last_name || '',
          stt: user?.stt?.name || '',
          hasFRAAccess: hasFRAAccess ?? null,
          regions: user?.regions || new Set(),
          jurisdictionType: user?.stt?.type || JURISDICTION_TYPES.STATE,
        }}
        onCancel={onCancel}
        type={type}
      />
    )
  }

  return (
    <UserProfileView
      user={user}
      isAMSUser={isAMSUser}
      isAccessRequestPending={isAccessRequestPending}
      onEdit={onEdit}
      type={type}
      hasFRAAccess={hasFRAAccess ?? null}
    />
  )
}

export default Profile
