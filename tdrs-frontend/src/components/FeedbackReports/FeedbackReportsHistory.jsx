import React from 'react'
import PropTypes from 'prop-types'
import { Spinner } from '../Spinner'

/**
 * FeedbackReportsHistory component displays the upload history table
 * with loading and empty states
 */
function FeedbackReportsHistory({ data, formatDateTime }) {
  return (
    <table className="usa-table usa-table--striped">
      <caption>Upload History</caption>
      {data && data.length > 0 ? (
        <>
          <thead>
            <tr>
              <th>Fiscal year</th>
              <th>Feedback uploaded on</th>
              <th>Notifications sent on</th>
              <th>Status</th>
              <th style={{ minWidth: '200px' }}>Error</th>
              <th>File</th>
            </tr>
          </thead>
          <tbody>
            {data.map((report) => (
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
        <tbody>
          <tr>
            <td
              colSpan="6"
              style={{
                border: '0',
                backgroundColor: 'white',
                padding: '0',
              }}
            >
              No data available.
            </td>
          </tr>
        </tbody>
      )}
    </table>
  )
}

FeedbackReportsHistory.propTypes = {
  data: PropTypes.array,
  formatDateTime: PropTypes.func.isRequired,
}

export default FeedbackReportsHistory
