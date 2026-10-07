import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faCheckCircle,
  faXmarkCircle,
  faClock,
} from '@fortawesome/free-solid-svg-icons'
import NotesModal from './NotesModal'

/**
 * ReportSourceStatusIcon displays a status icon for report source processing states.
 */
function ReportSourceStatusIcon({ status }) {
  let icon = null
  let color = null

  switch (status) {
    case 'PENDING':
    case 'PROCESSING':
      icon = faClock
      color = '#005EA2'
      break
    case 'SUCCEEDED':
      icon = faCheckCircle
      color = '#40bb45'
      break
    case 'FAILED':
      icon = faXmarkCircle
      color = '#bb0000'
      break
    default:
      break
  }

  if (!icon) return null

  return (
    <FontAwesomeIcon className="margin-right-1" icon={icon} color={color} />
  )
}

ReportSourceStatusIcon.propTypes = {
  status: PropTypes.string,
}

/**
 * formatStatusDisplay converts status to display format.
 * SUCCEEDED becomes "Parsed & Notified", others become title case.
 */
function formatStatusDisplay(status) {
  if (status === 'SUCCEEDED') {
    return 'Parsed & Notified'
  }
  if (!status) return ''
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase()
}

/**
 * formatDate formats a date string (YYYY-MM-DD) to MM/DD/YYYY
 */
function formatDate(dateString) {
  if (!dateString) return 'N/A'
  const date = new Date(dateString + 'T00:00:00')
  return date.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
  })
}

/**
 * FeedbackReportsHistory component displays the upload history table
 * with loading and empty states
 */
function FeedbackReportsHistory({
  data,
  formatDateTime,
  onViewDownloadStatistics,
}) {
  const [activeNotesReport, setActiveNotesReport] = useState(null)

  return (
    <>
      <table className="usa-table usa-table--striped" style={{ width: '100%' }}>
        <caption>Upload History</caption>
        {data && data.length > 0 ? (
          <>
            <thead>
              <tr>
                <th>Feedback Uploaded On</th>
                <th>Data Extracted On</th>
                <th>Notifications Sent On</th>
                <th>Status</th>
                <th style={{ minWidth: '200px' }}>Error</th>
                <th>File</th>
                <th>Downloaded by</th>
                <th
                  style={{
                    width: '100ch',
                    minWidth: '100ch',
                    maxWidth: '100ch',
                    whiteSpace: 'normal',
                  }}
                >
                  Notes
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((report) => (
                <tr key={report.id} style={{ verticalAlign: 'top' }}>
                  <td>{formatDateTime(report.created_at)}</td>
                  <td>{formatDate(report.date_extracted_on)}</td>
                  <td>{formatDateTime(report.processed_at)}</td>
                  <td style={{ textWrap: 'nowrap' }}>
                    <ReportSourceStatusIcon status={report.status} />
                    {formatStatusDisplay(report.status)}
                  </td>
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
                  <td>
                    <button
                      type="button"
                      className="usa-button usa-button--unstyled text-no-wrap"
                      aria-label={`View download statistics for ${
                        report.original_filename || `report source ${report.id}`
                      }`}
                      onClick={() => onViewDownloadStatistics(report.id)}
                    >
                      {report.downloaded_count || 0}{' '}
                      {report.downloaded_count === 1
                        ? 'jurisdiction'
                        : 'jurisdictions'}
                    </button>
                  </td>
                  <td
                    style={{
                      width: '100ch',
                      minWidth: '100ch',
                      maxWidth: '100ch',
                      whiteSpace: 'normal',
                    }}
                  >
                    {report.notes ? (
                      <div
                        style={{
                          width: '100ch',
                          minWidth: '100ch',
                          maxWidth: '100ch',
                          whiteSpace: 'normal',
                        }}
                      >
                        <span
                          style={{
                            whiteSpace: 'normal',
                            wordBreak: 'break-word',
                            overflowWrap: 'break-word',
                          }}
                        >
                          {report.notes.length > 290 ? (
                            <>
                              {report.notes.slice(0, 290)}
                              <button
                                type="button"
                                className="usa-button usa-button--unstyled notes-read-more-button"
                                style={{
                                  display: 'inline',
                                  outline: 'none',
                                  boxShadow: 'none',
                                }}
                                aria-label={`Read more notes for ${
                                  report.original_filename ||
                                  `report source ${report.id}`
                                }`}
                                onClick={() => setActiveNotesReport(report)}
                              >
                                ...
                              </button>
                            </>
                          ) : (
                            report.notes
                          )}
                        </span>
                      </div>
                    ) : (
                      'No Notes'
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
                colSpan="8"
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

      {activeNotesReport && (
        <NotesModal
          filename={activeNotesReport.original_filename}
          notes={activeNotesReport.notes}
          onClose={() => setActiveNotesReport(null)}
        />
      )}
    </>
  )
}

FeedbackReportsHistory.propTypes = {
  data: PropTypes.array,
  formatDateTime: PropTypes.func.isRequired,
  onViewDownloadStatistics: PropTypes.func.isRequired,
}

export default FeedbackReportsHistory
