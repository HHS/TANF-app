import React from 'react'
import PropTypes from 'prop-types'

/**
 * FeedbackReportsHistory component displays the upload history table
 * with loading and empty states
 */
function FeedbackReportsHistory({ uploadHistory, isLoading, formatDateTime }) {
  if (isLoading) {
    return (
      <div className="padding-y-3 text-center">
        <p className="text-base">Loading upload history...</p>
      </div>
    )
  }

  return (
    <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
      <caption>Upload History</caption>
      {uploadHistory.length > 0 ? (
        <>
          <thead>
            <tr>
              <th>Fiscal year</th>
              <th>Feedback uploaded on</th>
              <th>Notifications sent on</th>
              <th>Status</th>
              <th>Error</th>
              <th>File</th>
            </tr>
          </thead>
          <tbody>
            {uploadHistory.map((report) => (
              <tr key={report.id}>
                <td>{report.year || new Date().getFullYear()}</td>
                <td>{formatDateTime(report.created_at)}</td>
                <td>{formatDateTime(report.processed_at)}</td>
                <td>{report.status}</td>
                <td>{report.error_message || 'None'}</td>
                <td>
                  {report.original_filename ? (
                    <a
                      href={report.file}
                      download={report.original_filename}
                      className="usa-link"
                    >
                      {report.original_filename}
                    </a>
                  ) : (
                    'N/A'
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </>
      ) : (
        <span>No data available.</span>
      )}
    </table>
  )
}

FeedbackReportsHistory.propTypes = {
  uploadHistory: PropTypes.array.isRequired,
  isLoading: PropTypes.bool.isRequired,
  formatDateTime: PropTypes.func.isRequired,
}

export default FeedbackReportsHistory
