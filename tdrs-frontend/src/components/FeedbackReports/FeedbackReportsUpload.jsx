import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import { fileInput, datePicker } from '@uswds/uswds/src/js/components'
import Button from '../Button'

const INVALID_EXT_ERROR = 'Invalid file. Make sure to select a zip file.'

/**
 * FeedbackReportsUpload component handles the file upload section
 * for feedback reports
 */
function FeedbackReportsUpload({
  selectedFile,
  fileError,
  loading,
  onFileChange,
  onUpload,
  inputRef,
  dateExtractedOn,
  dateError,
  onDateChange,
  onDateBlur,
}) {
  const formattedSectionName = 'feedback_reports'
  const ariaDescription = selectedFile
    ? `Selected File ${selectedFile.name}. To change the selected file, click this button.`
    : 'Drag file here or choose from folder.'

  useEffect(() => {
    fileInput.init()
    datePicker.init()
  }, [])

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
            className={`usa-input ${dateError ? 'usa-input--error' : ''}`}
            id="date-extracted-on"
            name="date-extracted-on"
            aria-labelledby="date-extracted-on-label"
            aria-describedby="date-extracted-hint"
            value={dateExtractedOn}
            onChange={onDateChange}
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
}

FeedbackReportsUpload.propTypes = {
  selectedFile: PropTypes.object,
  fileError: PropTypes.string,
  loading: PropTypes.bool.isRequired,
  onFileChange: PropTypes.func.isRequired,
  onUpload: PropTypes.func.isRequired,
  inputRef: PropTypes.object.isRequired,
  dateExtractedOn: PropTypes.string,
  dateError: PropTypes.string,
  onDateChange: PropTypes.func,
  onDateBlur: PropTypes.func,
}

export default FeedbackReportsUpload
