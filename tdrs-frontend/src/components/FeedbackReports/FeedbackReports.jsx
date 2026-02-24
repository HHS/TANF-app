import { useSelector } from 'react-redux'
import { accountCanUploadFeedbackReports } from '../../selectors/auth'
import AdminFeedbackReports from './AdminFeedbackReports'
import STTFeedbackReports from './STTFeedbackReports'

/**
 * FeedbackReports wrapper component that conditionally renders
 * the appropriate view based on user permissions.
 *
 * - Admin users (with upload permissions) see the upload interface
 * - STT Data Analysts see the read-only view with download capability
 */
function FeedbackReports() {
  const canUpload = useSelector(accountCanUploadFeedbackReports)

  if (canUpload) {
    return <AdminFeedbackReports />
  }

  return <STTFeedbackReports />
}

export default FeedbackReports
