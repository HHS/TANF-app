import React, { useState } from 'react'
import PropTypes from 'prop-types'
import axiosInstance from '../../axios-instance'

/**
 * Formats a timestamp to a readable date string
 */
const formatDateTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp)
  return date.toLocaleString('en-US', {
    month: '2-digit',
    day: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

/**
 * STTFeedbackReportsTable component displays the feedback reports table
 * for STT Data Analysts with download functionality
 */
function STTFeedbackReportsTable({ data, setAlert }) {
  const [downloadingId, setDownloadingId] = useState(null)

  /**
   * Handle file download
   */
  const handleDownload = async (report) => {
    setDownloadingId(report.id)
    setAlert({ active: false, type: null, message: null })

    try {
      const response = await axiosInstance.get(
        `${process.env.REACT_APP_BACKEND_URL}/reports/${report.id}/download/`,
        {
          responseType: 'blob',
          withCredentials: true,
        }
      )

      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', report.original_filename || 'report.zip')
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download report:', error)
      setAlert({
        active: true,
        type: 'error',
        message: 'Failed to download the report. Please try again.',
      })
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <table className="usa-table usa-table--striped">
      {data && data.length > 0 ? (
        <>
          <thead>
            <tr>
              <th>Feedback generated on</th>
              <th>Fiscal quarters included in feedback</th>
              <th>Files</th>
            </tr>
          </thead>
          <tbody>
            {data.map((report) => (
              <tr key={report.id}>
                <td>{formatDateTime(report.created_at)}</td>
                <td>{report.quarter}</td>
                <td>
                  <button
                    type="button"
                    className="usa-button usa-button--unstyled"
                    onClick={() => handleDownload(report)}
                    disabled={downloadingId === report.id}
                    aria-label={`Download ${report.original_filename}`}
                  >
                    {downloadingId === report.id
                      ? 'Downloading...'
                      : report.original_filename || 'Download'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </>
      ) : (
        <tbody>
          <tr>
            <td
              colSpan="3"
              style={{
                border: '0',
                backgroundColor: 'white',
                padding: '1rem 0',
              }}
            >
              No feedback reports available for this fiscal year.
            </td>
          </tr>
        </tbody>
      )}
    </table>
  )
}

STTFeedbackReportsTable.propTypes = {
  data: PropTypes.array,
  setAlert: PropTypes.func.isRequired,
}

export default STTFeedbackReportsTable
