import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import ResourceCards from '../ResourceCards'
import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import {
  accountStatusIsApproved,
  accountIsInReview,
} from '../../selectors/auth'
import Profile from '../Profile/Profile'

/**
 * Home renders the Request Access form for creating a profile, and displays
 * a pending-approval state, before showing the user their active roles and
 * permissions once they are approved by an Admin in the backend.
 */
function Home({ setInEditMode }) {
  const user = useSelector((state) => state.auth.user)
  const sttList = useSelector((state) => state?.stts?.sttList)

  const userAccessInReview = useSelector(accountIsInReview)
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)

  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    setInEditMode(isEditing, 'access request')
  }, [isEditing, setInEditMode])

  if (userAccessInReview) {
    return (
      <Profile
        isEditing={isEditing}
        onEdit={() => setIsEditing(true)}
        type="access request"
        user={user}
        sttList={sttList}
        onCancel={() => setIsEditing(false)}
      />
    )
  } else if (!userAccessRequestApproved) {
    return <RequestAccessForm user={user} sttList={sttList} />
  }

  return (
    <>
      <div className="margin-top-5">
        <p className="margin-top-1 margin-bottom-4">
          You have been approved for access to TDP. For guidance on submitting
          data, managing your account, and utilizing other functionality please
          refer to the TDP Knowledge Center.
        </p>
      </div>
      <br />
      <hr />
      <br />
      <ResourceCards />
    </>
  )
}

export default Home
