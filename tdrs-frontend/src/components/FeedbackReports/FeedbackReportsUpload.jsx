import React from 'react'
import PropTypes from 'prop-types'
import Button from '../Button'

const INVALID_EXT_ERROR = 'File must be a .zip file'

/**
 * FeedbackReportsUpload component handles the file upload section
 * for quarterly feedback reports
 */
function FeedbackReportsUpload({
  selectedFile,
  fileError,
  loading,
  onFileChange,
  onUpload,
  inputRef,
}) {
  const formattedSectionName = 'feedback_reports'
  const ariaDescription = selectedFile
    ? `Selected File ${selectedFile.name}. To change the selected file, click this button.`
    : 'Drag file here or choose from folder.'

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
        accept=".zip"
        aria-describedby={`${formattedSectionName}-file`}
        aria-hidden="false"
        data-errormessage={INVALID_EXT_ERROR}
      />

      <Button
        type="submit"
        onClick={onUpload}
        disabled={!selectedFile || loading}
        className="margin-top-2"
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
}

export default FeedbackReportsUpload
