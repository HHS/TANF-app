import React from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useSelector } from 'react-redux'
import signOut from '../../utils/signOut'
import ResourceCards from '../ResourceCards'
import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import {
  accountStatusIsApproved,
  accountIsInReview,
} from '../../selectors/auth'

/**
 * Home renders the Request Access form for creating a profile, and displays
 * a pending-approval state, before showing the user their active roles and
 * permissions once they are approved by an Admin in the backend.
 */
function Home() {
  const user = useSelector((state) => state.auth.user)
  const sttList = useSelector((state) => state?.stts?.sttList)

  const userAccessInReview = useSelector(accountIsInReview)
  const userAccessRequestApproved = useSelector(accountStatusIsApproved)

  if (userAccessInReview) {
    return (
      <div className="margin-top-5">
        <div className="margin-top-5">
          <p className="margin-top-1 margin-bottom-4" id="page-alert">
            Your request for access is currently being reviewed by an OFA Admin.
            We'll send you an email when it's been approved.
          </p>
        </div>
        <Button type="button" onClick={signOut}>
          <FontAwesomeIcon className="margin-right-1" icon={faSignOutAlt} />
          Sign Out
        </Button>
      </div>
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
