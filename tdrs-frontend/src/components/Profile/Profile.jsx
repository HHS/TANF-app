import React, { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import UserProfileView from './UserProfileView'
import {
  accountIsInReview,
  accountIsMissingAccessRequest,
} from '../../selectors/auth'

/**
 * Profile handles rendering user information in a read-only or editable mode.
 * It is reused for both:
 * - Viewing/editing an access request form (in the Home page context)
 * - Viewing/editing a user profile (in the Profile page context)
 *
 * Props:
 * - isEditing: Boolean to toggle edit mode
 * - onEdit: Function to trigger editing
 * - onCancel: Function to cancel editing
 * - user: The user object from Redux
 * - sttList: (Optional) list of STTs for access form
 * - type: 'profile' or 'access request'
 */
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
  const missingAccessRequest = useSelector(accountIsMissingAccessRequest)
  const isAccessRequestPending = useSelector(accountIsInReview)
  //const isAccessRequestPending = true // TODO: using for testing

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
        editMode={true}
        initialValues={{
          firstName: user?.first_name || '',
          lastName: user?.last_name || '',
          stt: user?.stt?.name || '',
          hasFRAAccess: user?.permissions?.includes('has_fra_access') ?? null,
          regions: user?.stt?.regions || new Set(),
          jurisdictionType: user?.stt?.type || 'state',
        }}
        onCancel={onCancel}
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
    />
  )
}

export default Profile
