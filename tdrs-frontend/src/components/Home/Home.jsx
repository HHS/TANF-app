import React, { useEffect, useState } from 'react'
import { useSelector } from 'react-redux'
import ResourceCards from '../ResourceCards'
import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import {
  accountStatusIsApproved,
  accountIsInReview,
} from '../../selectors/auth'
import UserAccessInfo from '../UserAccessInfo'

/**
 * Home renders the Request Access form for creating a profile, and displays
 * a pending-approval state, before showing the user their active roles and
 * permissions once they are approved by an Admin in the backend.
 */
function Home({ setInEditMode }) {
  const user = useSelector((state) => state.auth.user)
  const sttList = useSelector((state) => state?.stts?.sttList)

  // TODO: only changing for testing
  //const userAccessInReview = useSelector(accountIsInReview)
  const userAccessInReview = true
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)

  const [isEditing, setIsEditing] = useState(false)

  useEffect(() => {
    setInEditMode(isEditing)
  }, [isEditing, setInEditMode])

  if (userAccessInReview) {
    if (isEditing) {
      // TODO: may need to add a submit Updated Request Access profile
      // TODO: may need to play around with initial values
      return (
        <RequestAccessForm
          user={user}
          sttList={sttList}
          editMode={true}
          initialValues={{
            firstName: user?.first_name,
            lastName: user?.last_name,
            stt: user?.stt?.name,
            hasFRAAccess:
              user?.permissions?.includes('has_fra_access') === 'Yes',
            jurisdictionType: user?.stt?.type,
            regions: user?.regions,
          }}
          onCancel={() => setIsEditing(false)}
        />
      )
    }

    return (
      <div className="margin-top-5">
        <div className="margin-top-5">
          <div
            className="usa-alert usa-alert--slim usa-alert--info margin-top-1 margin-bottom-4 margin-right-4"
            id="page-alert"
          >
            <div className="usa-alert__body" role="alert">
              <p className="usa-alert__text">
                Your request for access is currently being reviewed by an OFA
                Admin. We'll send you an email when it's been approved.
              </p>
            </div>
          </div>
        </div>
        <UserAccessInfo onEditClick={() => setIsEditing(true)} />
      </div>
    )
  } else if (!userAccessRequestApproved) {
    return (
      // TODO: may need to play aroudn with initial values
      <RequestAccessForm user={user} sttList={sttList} />
    )
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
