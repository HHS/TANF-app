import React from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'

import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import UserProfileView from './UserProfileView'
import {
  accountIsInReview,
  accountIsMissingAccessRequest,
} from '../../selectors/auth'

function Profile({ isEditing = false, onEdit, type, user, sttList, onCancel }) {
  const isAMSUser = user?.email?.includes('@acf.hhs.gov')
  const missingAccessRequest = useSelector(accountIsMissingAccessRequest)
  const isAccessRequestPending = useSelector(accountIsInReview)
  //const isAccessRequestPending = true // TODO: using for testing

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
          regions: user?.regions || new Set(),
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
