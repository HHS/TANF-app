import { useState, useEffect, useRef, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import axiosInstance from '../../axios-instance'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import FeedbackReportsUpload from './FeedbackReportsUpload'
import FeedbackReportsHistory from './FeedbackReportsHistory'
import { PaginatedComponent } from '../Paginator/Paginator'
import { Spinner } from '../Spinner'
import { constructYears } from '../Reports/utils'

const INVALID_EXT_ERROR = 'Invalid file. Make sure to select a zip file.'
const NO_FILE_ERROR = 'No file selected.'
const FY_MISMATCH_ERROR =
  "Your file's Fiscal Year does not match the selected Fiscal Year for this upload."
const NO_DATE_ERROR =
  "Choose the date that the data you're uploading was extracted from the database."

/**
 * AdminFeedbackReports component allows OFA Admins to upload quarterly feedback reports
 * as ZIP files that will be distributed to State/Tribal TANF Programs (STTs).
 */
function AdminFeedbackReports() {
  const [searchParams, setSearchParams] = useSearchParams()
  const yearOptions = constructYears()

  // Get validated year from URL params (returns null if not present/invalid)
  const getValidatedYear = () => {
    const urlYear = searchParams.get('year')
    if (!urlYear) return null
    const parsedYear = parseInt(urlYear, 10)
    if (!isNaN(parsedYear) && yearOptions.includes(parsedYear)) {
      return parsedYear
    }
    return null
  }

  const [selectedYear, setSelectedYear] = useState(getValidatedYear)
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
  const [dateError, setDateError] = useState(null)
  const [formSubmitAttempted, setFormSubmitAttempted] = useState(false)
  const [dateTouched, setDateTouched] = useState(false)

  const inputRef = useRef(null)
  const uploadFormRef = useRef(null)

  /**
   * Fetches the upload history from the backend filtered by selected year
   */
  const fetchUploadHistory = useCallback(async () => {
    if (!selectedYear) {
      setUploadHistory([])
      return
    }

    setHistoryLoading(true)
    try {
      const response = await axiosInstance.get(
        `${process.env.REACT_APP_BACKEND_URL}/reports/report-sources/`,
        {
          params: { year: selectedYear },
          withCredentials: true,
        }
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
  }, [selectedYear])

  // Fetch upload history when year changes
  useEffect(() => {
    fetchUploadHistory()
  }, [fetchUploadHistory])

  /**
   * Extracts the fiscal year from a filename like "FY2025_12012025.zip"
   * Returns null if the pattern doesn't match
   */
  const extractFYFromFilename = (filename) => {
    const match = filename.match(/^FY(\d{4})/i)
    return match ? parseInt(match[1], 10) : null
  }

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

    // Validate fiscal year in filename matches selected fiscal year
    const fileFY = extractFYFromFilename(fileInputValue.name)
    if (fileFY && selectedYear && fileFY !== parseInt(selectedYear, 10)) {
      createFileInputErrorState(input, dropTarget)
      setFileError(FY_MISMATCH_ERROR)
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
   * Gets the date value from the upload form's date picker
   */
  const getDatePickerValue = () => {
    return uploadFormRef.current?.getDateValue() || ''
  }

  /**
   * Clears the upload form's date picker
   */
  const clearDatePicker = () => {
    uploadFormRef.current?.clearDate()
  }

  /**
   * Validates the form before upload
   * Returns true if valid, false otherwise
   */
  const validateForm = () => {
    let isValid = true
    setFormSubmitAttempted(true)

    if (!selectedFile) {
      setFileError(NO_FILE_ERROR)
      isValid = false
    }

    // Read date directly from DOM since USWDS manages the input
    const dateValue = getDatePickerValue()
    if (!dateValue) {
      setDateError(NO_DATE_ERROR)
      isValid = false
    }

    return isValid
  }

  /**
   * Handles the file upload to the backend
   */
  const handleUpload = async () => {
    if (!validateForm()) return

    setLoading(true)
    setAlert({ active: false, type: null, message: null })

    const formData = new FormData()
    formData.append('file', selectedFile)
    formData.append('year', selectedYear)
    formData.append('date_extracted_on', getDatePickerValue())

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

      // Clear the form
      setSelectedFile(null)
      setFileError(null)
      clearDatePicker()
      setDateError(null)
      setFormSubmitAttempted(false)
      setDateTouched(false)

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
   * Handles fiscal year selection change
   */
  const handleYearChange = (e) => {
    const newYear = e.target.value || null
    setSelectedYear(newYear)
    // Reset form state when year changes
    setSelectedFile(null)
    setFileError(null)
    clearDatePicker()
    setDateError(null)
    setFormSubmitAttempted(false)
    setDateTouched(false)
    setAlert({ active: false, type: null, message: null })
    // Update URL param
    if (newYear) {
      setSearchParams({ year: newYear }, { replace: true })
    } else {
      setSearchParams({}, { replace: true })
    }
  }

  /**
   * Handles date input blur - reads from DOM since USWDS manages the input
   */
  const handleDateBlur = () => {
    setDateTouched(true)
    if (!getDatePickerValue()) {
      setDateError(NO_DATE_ERROR)
    } else {
      setDateError(null)
    }
  }

  // Determine if we should show date error
  const showDateError = dateError && (dateTouched || formSubmitAttempted)

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

        {/* Fiscal Year Selector */}
        <div className="usa-form-group maxw-mobile margin-top-4">
          <label className="usa-label text-bold" htmlFor="fiscal-year-select">
            Fiscal Year
          </label>
          <select
            className="usa-select maxw-mobile"
            id="fiscal-year-select"
            value={selectedYear || ''}
            onChange={handleYearChange}
          >
            <option value="">- Select Fiscal Year -</option>
            {yearOptions.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Conditional content - only show when fiscal year is selected */}
        {selectedYear && (
          <>
            <hr className="margin-top-4 margin-bottom-4" />

            <h2 className="margin-top-0 margin-bottom-4">
              Fiscal Year {selectedYear} — Upload Feedback Reports
            </h2>

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
              ref={uploadFormRef}
              selectedFile={selectedFile}
              fileError={fileError}
              loading={loading}
              onFileChange={handleFileChange}
              onUpload={handleUpload}
              inputRef={inputRef}
              dateError={showDateError ? dateError : null}
              onDateBlur={handleDateBlur}
            />

            {/* Upload History Section */}
            <div className="submission-history-section usa-table-container">
              {historyLoading ? (
                <div className="submission-history-section-spinner margin-y-3">
                  <Spinner visible={true} />
                  <span className="margin-left-1">
                    Loading upload history...
                  </span>
                </div>
              ) : (
                <PaginatedComponent pageSize={10} data={uploadHistory}>
                  <FeedbackReportsHistory formatDateTime={formatDateTime} />
                </PaginatedComponent>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default AdminFeedbackReports
