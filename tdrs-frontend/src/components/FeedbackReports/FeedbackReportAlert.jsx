import React from 'react'
import PropTypes from 'prop-types'

/**
 * Alert banner displayed on TANF Data Files page when feedback reports are available.
 * Only shown to Data Analysts when reports exist for their STT and selected quarter/year.
 */
const FeedbackReportAlert = ({ latestReportDate = null }) => {
  if (!latestReportDate) return null

  // Format date as MM/DD/YYYY
  const formattedDate = new Date(latestReportDate).toLocaleDateString('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
  })

  return (
    <div className="usa-alert usa-alert--info margin-top-4 margin-bottom-4">
      <div className="usa-alert__body">
        <p className="usa-alert__text">
          Feedback Reports Available as of {formattedDate}. Please{' '}
          <a href="/feedback-reports">review the feedback</a> and if needed,
          resubmit complete and accurate data.
        </p>
      </div>
    </div>
  )
}

FeedbackReportAlert.propTypes = {
  latestReportDate: PropTypes.string,
}

export default FeedbackReportAlert
