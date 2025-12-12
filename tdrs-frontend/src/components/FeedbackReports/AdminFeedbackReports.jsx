import { useState, useEffect, useRef, useCallback } from 'react'
import axiosInstance from '../../axios-instance'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import { fileInput } from '@uswds/uswds/src/js/components'
import FeedbackReportsUpload from './FeedbackReportsUpload'
import FeedbackReportsHistory from './FeedbackReportsHistory'
import { PaginatedComponent } from '../Paginator/Paginator'
import { Spinner } from '../Spinner'

const INVALID_EXT_ERROR = 'File must be a .zip file'

/**
 * AdminFeedbackReports component allows OFA Admins to upload quarterly feedback reports
 * as ZIP files that will be distributed to State/Tribal TANF Programs (STTs).
 */
function AdminFeedbackReports() {
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

  /**
   * Fetches the upload history from the backend
   */
  const fetchUploadHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const response = await axiosInstance.get(
        `${process.env.REACT_APP_BACKEND_URL}/reports/report-sources/`,
        { withCredentials: true }
      )
      setUploadHistory(response.data.results)
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
  }, [])

  // Initialize USWDS file input component and fetch upload history on mount
  useEffect(() => {
    fileInput.init()
    fetchUploadHistory()
  }, [fetchUploadHistory])

  /**
   * Handles file selection from the file input
   */
  const handleFileChange = async (e) => {
    setSelectedFile(null)
    setFileError(null)
    setAlert({ active: false, type: null, message: null })

    const fileInputValue = e.target.files[0]
    if (!fileInputValue) return

    const input = inputRef.current
    const dropTarget = input.parentNode

    // Read file to allow USWDS time to create preview elements
    const loadFile = () =>
      new Promise((resolve, reject) => {
        const filereader = new FileReader()
        filereader.onerror = () => {
          filereader.abort()
          reject(new Error('Problem loading input file'))
        }
        filereader.onload = () => resolve()
        filereader.readAsArrayBuffer(fileInputValue)
      })

    await loadFile()

    // Validate file extension after USWDS has created preview
    const zipExtension = /(\.zip)$/i
    const isZip = zipExtension.exec(fileInputValue.name)

    if (!isZip) {
      createFileInputErrorState(input, dropTarget)
      setFileError(INVALID_EXT_ERROR)
      return
    }

    // Clean up any leftover error state from previous invalid file
    const instructions = dropTarget.querySelector(
      '.usa-file-input__instructions'
    )
    if (instructions) {
      instructions.classList.remove('display-block')
    }
    dropTarget.classList.remove('has-invalid-file')

    setSelectedFile(fileInputValue)
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

        <hr className="margin-top-2 margin-bottom-2" />

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

        {/* File Upload Section */}
        <FeedbackReportsUpload
          selectedFile={selectedFile}
          fileError={fileError}
          loading={loading}
          onFileChange={handleFileChange}
          onUpload={handleUpload}
          inputRef={inputRef}
        />

        {/* Upload History Section */}
        <div className="submission-history-section usa-table-container">
          {historyLoading ? (
            <div className="submission-history-section-spinner margin-y-3">
              <Spinner visible={true} />
              <span className="margin-left-1">Loading upload history...</span>
            </div>
          ) : (
            <PaginatedComponent pageSize={5} data={uploadHistory}>
              <FeedbackReportsHistory formatDateTime={formatDateTime} />
            </PaginatedComponent>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminFeedbackReports
