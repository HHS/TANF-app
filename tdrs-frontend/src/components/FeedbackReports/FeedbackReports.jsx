import { useState, useEffect, useRef } from 'react'
import { useSelector } from 'react-redux'
import { Navigate } from 'react-router-dom'
import Button from '../Button'
import axiosInstance from '../../axios-instance'
import { accountCanViewAdmin } from '../../selectors/auth'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import { fileInput } from '@uswds/uswds/src/js/components'

const INVALID_EXT_ERROR = 'File must be a .zip file'

/**
 * FeedbackReports component allows OFA Admins to upload quarterly feedback reports
 * as ZIP files that will be distributed to State/Tribal TANF Programs (STTs).
 */
function FeedbackReports() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploadHistory, setUploadHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(false)
  const [alert, setAlert] = useState({
    active: false,
    type: null,
    message: null,
  })

  const [fileError, setFileError] = useState(null)

  const inputRef = useRef(null)
  const user = useSelector((state) => state.auth.user)
  const userIsAdmin = useSelector(accountCanViewAdmin)

  // Initialize USWDS file input component
  useEffect(() => {
    fileInput.init()
  }, [])

  // Fetch upload history on component mount
  useEffect(() => {
    fetchUploadHistory()
  }, [])

  // Redirect non-admin users (after all hooks)
  if (!userIsAdmin) {
    return <Navigate to="/home" />
  }

  /**
   * Fetches the upload history from the backend
   */
  const fetchUploadHistory = async () => {
    setHistoryLoading(true)
    try {
      const response = await axiosInstance.get(
        `${process.env.REACT_APP_BACKEND_URL}/reports/report-sources/`,
        { withCredentials: true }
      )
      setUploadHistory(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to fetch upload history:', error)
      setAlert({
        active: true,
        type: 'error',
        message: 'Failed to load upload history. Please refresh the page.',
      })
    } finally {
      setHistoryLoading(false)
    }
  }

  const formattedSectionName = 'feedback_reports'
  const ariaDescription = selectedFile
    ? `Selected File ${selectedFile.name}. To change the selected file, click this button.`
    : 'Drag file here or choose from folder.'

  /**
   * Handles file selection from the file input
   */
  const handleFileChange = (e) => {
    setAlert({ active: false, type: null, message: null })
    setFileError(null)

    const file = e.target.files[0]
    if (!file) {
      setSelectedFile(null)
      return
    }

    const input = inputRef.current
    const dropTarget = inputRef.current?.parentNode

    // Validate file extension
    const re = /\.zip$/i
    if (!re.exec(file.name)) {
      createFileInputErrorState(input, dropTarget)
      setFileError(INVALID_EXT_ERROR)
      setSelectedFile(null)
      return
    }

    setSelectedFile(file)
    inputRef.current.value = null
  }

  /**
   * Handles the file upload to the backend
   */
  const handleUpload = async () => {
    if (!selectedFile) return

    setLoading(true)
    setAlert({ active: false, type: null, message: null })

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      await axiosInstance.post(
        `${process.env.REACT_APP_BACKEND_URL}/reports/report-sources/`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true,
        }
      )

      setAlert({
        active: true,
        type: 'success',
        message:
          'Feedback report uploaded successfully! Processing has begun and states will be notified once complete.',
      })

      // Clear the file input
      setSelectedFile(null)
      setFileError(null)

      // Refresh upload history
      fetchUploadHistory()
    } catch (error) {
      const errorMessage =
        error.response?.data?.file?.[0] ||
        error.response?.data?.detail ||
        error.response?.data?.message ||
        'Upload failed. Please try again.'

      setAlert({
        active: true,
        type: 'error',
        message: errorMessage,
      })
    } finally {
      setLoading(false)
    }
  }

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
   * Gets the status badge for a report
   */
  const getStatusBadge = (status) => {
    const statusMap = {
      PENDING: { label: 'Pending', className: 'bg-base-lighter text-ink' },
      PROCESSING: { label: 'Processing', className: 'bg-gold-20v text-ink' },
      SUCCEEDED: {
        label: 'Complete',
        className: 'bg-success-lighter text-ink',
      },
      FAILED: { label: 'Failed', className: 'bg-error-lighter text-ink' },
    }

    const statusInfo = statusMap[status] || statusMap.PENDING
    return (
      <span
        className={`usa-tag ${statusInfo.className} padding-x-1 padding-y-05 font-sans-3xs text-bold radius-md`}
      >
        {statusInfo.label}
      </span>
    )
  }

  return (
    <div className="feedback-reports">
      <div className="page-container" style={{ position: 'relative' }}>
        {/* Description */}
        <p className="margin-top-5 margin-bottom-0">
          Once submitted, TDP will distribute feedback reports to TANF/SSP
          submission history pages of each state and notify users that feedback
          reports are available. There may be several minutes between when the
          ZIP is uploaded and when all notifications have been sent as TDP
          processes the reports.
        </p>

        {/* Alert Messages */}
        {alert.active && (
          <div
            className={`usa-alert usa-alert--${alert.type} usa-alert--slim margin-bottom-3`}
            role="alert"
          >
            <div className="usa-alert__body">
              <p className="usa-alert__text">{alert.message}</p>
            </div>
          </div>
        )}

        <hr className="margin-top-2 margin-bottom-2" />

        {/* File Upload Section */}
        <div
          className={`usa-form-group ${fileError ? 'usa-form-group--error' : ''}`}
        >
          <label className="usa-label text-bold" htmlFor={formattedSectionName}>
            Feedback Reports ZIP
          </label>
          <div>
            {fileError && (
              <div
                className="usa-error-message"
                id={`${formattedSectionName}-error-alert`}
                role="alert"
              >
                {fileError}
              </div>
            )}
          </div>
          <div
            id={`${formattedSectionName}-file`}
            aria-hidden
            className="display-none"
          >
            {ariaDescription}
          </div>
          <input
            ref={inputRef}
            onChange={handleFileChange}
            id={formattedSectionName}
            className="usa-file-input"
            type="file"
            name="feedback-reports"
            accept=".zip"
            aria-describedby={`${formattedSectionName}-file`}
            aria-hidden="false"
            data-errormessage={INVALID_EXT_ERROR}
          />

          <Button
            type="submit"
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            className="margin-top-2"
          >
            {loading ? 'Uploading...' : 'Upload & Notify States'}
          </Button>
        </div>

        {/* Upload History Section */}
        {historyLoading ? (
          <div className="padding-y-3 text-center">
            <p className="text-base">Loading upload history...</p>
          </div>
        ) : uploadHistory.length === 0 ? (
          <div className="padding-y-3 text-center border-1px border-base-lighter radius-md">
            <p className="text-base-dark">No feedback reports uploaded yet</p>
          </div>
        ) : (
          <table className="usa-table usa-table--striped margin-top-4 desktop:width-tablet mobile:width-full">
            <caption>Upload History</caption>
            <thead>
              <tr>
                <th>Fiscal year</th>
                <th>Feedback uploaded on</th>
                <th>Notifications sent on</th>
                <th>File</th>
              </tr>
            </thead>
            <tbody>
              {uploadHistory.map((report) => (
                <tr key={report.id}>
                  <td>{report.year || new Date().getFullYear()}</td>
                  <td>{formatDateTime(report.created_at)}</td>
                  <td>{formatDateTime(report.processed_at)}</td>
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
          </table>
        )}
      </div>
    </div>
  )
}

export default FeedbackReports
