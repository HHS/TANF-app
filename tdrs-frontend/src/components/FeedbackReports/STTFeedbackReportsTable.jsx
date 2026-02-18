import React, { useState } from 'react'
import axiosInstance from '../../axios-instance'
import { downloadBlob } from '../../utils/fileDownload'

/**
 * Formats a timestamp to a readable date string with time
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
 * Formats a date string (YYYY-MM-DD) to MM/DD/YYYY
 */
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const [year, month, day] = dateString.split('-')
  return `${month}/${day}/${year}`
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

      downloadBlob(response.data, report.original_filename || 'report.zip')
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
              <th>Generated on</th>
              <th>Reflects data submitted through</th>
              <th>Files</th>
            </tr>
          </thead>
          <tbody>
            {data.map((report) => (
              <tr key={report.id}>
                <td>{formatDateTime(report.created_at)}</td>
                <td>{formatDate(report.date_extracted_on)}</td>
                <td>
                  <button
                    type="button"
                    className="usa-link"
                    onClick={() => handleDownload(report)}
                    disabled={downloadingId === report.id}
                    aria-label={`Download ${report.original_filename}`}
                    style={{
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: 'pointer',
                    }}
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

export default STTFeedbackReportsTable
