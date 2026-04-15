import React, { useEffect, useImperativeHandle, forwardRef } from 'react'
import PropTypes from 'prop-types'
import { fileInput, datePicker } from '@uswds/uswds/src/js/components'
import Button from '../Button'

const INVALID_EXT_ERROR = 'Invalid file. Make sure to select a zip file.'

/**
 * Converts a date string to YYYY-MM-DD format for the backend.
 */
const convertToISODate = (value) => {
  if (!value) return ''
  // Check if already in YYYY-MM-DD format
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value
  }
  // Convert from MM/DD/YYYY to YYYY-MM-DD
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
    const [month, day, year] = value.split('/')
    return `${year}-${month}-${day}`
  }
  // Return as-is if format is unknown
  return value
}

/**
 * FeedbackReportsUpload component handles the file upload section
 * for feedback reports
 */
const FeedbackReportsUpload = forwardRef(function FeedbackReportsUpload(
  {
    selectedFile,
    fileError,
    loading,
    onFileChange,
    onUpload,
    inputRef,
    dateError,
    onDateBlur,
  },
  ref
) {
  const formattedSectionName = 'feedback_reports'
  const ariaDescription = selectedFile
    ? `Selected File ${selectedFile.name}. To change the selected file, click this button.`
    : 'Drag file here or choose from folder.'

  useEffect(() => {
    fileInput.init()
    datePicker.init()
  }, [])

  /**
   * Gets the date value from the USWDS date picker input
   * and converts it to YYYY-MM-DD format for the backend.
   */
  const getDateValue = () => {
    // Try the hidden input first (original input that USWDS hides)
    const dateInput = document.getElementById('date-extracted-on')
    if (dateInput && dateInput.value) {
      return convertToISODate(dateInput.value)
    }
    // Fallback to the external input that USWDS creates
    const externalInput = document.querySelector(
      '.usa-date-picker__external-input'
    )
    if (externalInput && externalInput.value) {
      return convertToISODate(externalInput.value)
    }
    return ''
  }

  /**
   * Clears the USWDS date picker by clearing both the hidden input
   * and the visible external input that USWDS creates
   */
  const clearDate = () => {
    const dateInput = document.getElementById('date-extracted-on')
    if (dateInput) {
      dateInput.value = ''
    }
    const externalInput = document.querySelector(
      '.usa-date-picker__external-input'
    )
    if (externalInput) {
      externalInput.value = ''
    }
  }

  // Expose methods to parent component via ref
  useImperativeHandle(ref, () => ({
    getDateValue,
    clearDate,
  }))

  return (
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
        onChange={onFileChange}
        id={formattedSectionName}
        className="usa-file-input"
        type="file"
        name="feedback-reports"
        aria-describedby={`${formattedSectionName}-file`}
        aria-hidden="false"
        data-errormessage={INVALID_EXT_ERROR}
      />

      {/* Date Extracted Input */}
      <div
        className={`usa-form-group margin-top-3 ${dateError ? 'usa-form-group--error' : ''}`}
      >
        <label
          className="usa-label text-bold"
          id="date-extracted-on-label"
          htmlFor="date-extracted-on"
        >
          Data extracted from database on
        </label>
        <div className="usa-hint" id="date-extracted-hint">
          mm/dd/yyyy
        </div>
        {dateError && (
          <div
            className="usa-error-message"
            id="date-extracted-error"
            role="alert"
          >
            {dateError}
          </div>
        )}
        <div className="usa-date-picker">
          <input
            className="usa-input"
            id="date-extracted-on"
            name="date-extracted-on"
            aria-labelledby="date-extracted-on-label"
            aria-describedby="date-extracted-hint"
            onBlur={onDateBlur}
          />
        </div>
      </div>

      <Button
        type="submit"
        onClick={onUpload}
        disabled={loading}
        className="margin-top-3"
      >
        {loading ? 'Uploading...' : 'Upload & Notify States'}
      </Button>
    </div>
  )
})

FeedbackReportsUpload.propTypes = {
  selectedFile: PropTypes.object,
  fileError: PropTypes.string,
  loading: PropTypes.bool.isRequired,
  onFileChange: PropTypes.func.isRequired,
  onUpload: PropTypes.func.isRequired,
  inputRef: PropTypes.object.isRequired,
  dateError: PropTypes.string,
  onDateBlur: PropTypes.func,
}

export default FeedbackReportsUpload
