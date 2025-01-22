import React, { useRef, useState } from 'react'
import Button from '../Button'
import { faSignOutAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { useDispatch, useSelector } from 'react-redux'
import signOut from '../../utils/signOut'
import FormGroup from '../FormGroup'
import STTComboBox from '../STTComboBox'
import { requestAccess } from '../../actions/requestAccess'
import ResourceCards from '../ResourceCards'
import RequestAccessForm from '../RequestAccessForm/RequestAccessForm'
import {
  accountStatusIsApproved,
  accountIsInReview,
  selectPrimaryUserRole,
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
        <table className="usa-table usa-table--striped">
          <caption>
            <b> Data Reporting Deadlines </b>
          </caption>
          <thead>
            <tr>
              <th scope="col">Fiscal Quarter</th>
              <th scope="col">Calendar Period</th>
              <th scope="col">Due Date</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>1</td>
              <td>Oct 1 - Dec 31</td>
              <td>February 14</td>
            </tr>
            <tr>
              <td>2</td>
              <td>Jan 1 - Mar 31</td>
              <td>May 15</td>
            </tr>
            <tr>
              <td>3</td>
              <td>Apr 1 - Jun 30</td>
              <td>August 14</td>
            </tr>
            <tr>
              <td>4</td>
              <td>Jul 1 - Sep 30</td>
              <td>November 14</td>
            </tr>
          </tbody>
        </table>
      </div>
      <br />
      <hr />
      <br />
      <ResourceCards />
    </>
  )
}

export default Home
