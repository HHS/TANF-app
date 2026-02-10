import React from 'react'
import classNames from 'classnames'
import Button from '../Button'
import FileUpload from '../FileUpload'
import { fileUploadSections } from '../../reducers/reports'
import { useFileUploadForm } from '../../hooks/useFileUploadForm'

const SectionFileUploadForm = ({ stt }) => {
  const num_sections = stt === undefined ? 4 : stt.num_sections

  // No file transformation needed for section uploads
  const transformFiles = null

  // Format sections for success message (1, 2, 3, etc.)
  const formatSections = (uploadedFiles) => {
    const uploadedSections = uploadedFiles
      ? uploadedFiles
          .map((file) => fileUploadSections.indexOf(file.section) + 1)
          .join(', ')
          .split(' ')
      : []

    if (uploadedSections.length > 1) {
      uploadedSections.splice(uploadedSections.length - 1, 0, 'and')
    }

    return uploadedSections.join(' ')
  }

  // Generate submit payload for section uploads
  const getSubmitPayload = ({
    quarter,
    year,
    formattedSections,
    logger,
    setLocalAlertState,
    stt,
    uploadedFiles,
    user,
    fileType,
  }) => ({
    quarter,
    year,
    formattedSections,
    logger,
    setLocalAlertState,
    stt,
    uploadedFiles,
    user,
    ssp: fileType === 'ssp-moe',
    fileType,
  })

  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    uploadedFiles,
    localAlert,
    processingAlert,
    isSubmitting,
    alertRef,
    processingAlertRef,
    onSubmit,
    handleCancel,
    setLocalAlertState,
  } = useFileUploadForm({
    stt,
    transformFiles,
    formatSections,
    getSubmitPayload,
  })

  return (
    <>
      {/* Screen-reader announcer  */}
      <div className="usa-sr-only">
        <div role="status" aria-live="polite" aria-atomic="true">
          {localAlert.active ? localAlert.message : ''}
        </div>

        <div role="status" aria-live="polite" aria-atomic="true">
          {processingAlert.active ? processingAlert.message : ''}
        </div>
      </div>

      {/* Visible alerts (not in accessibility tree, prevents duplicate screen reads */}
      {localAlert.active && (
        <div
          className={classNames('usa-alert usa-alert--slim', {
            [`usa-alert--${localAlert.type}`]: true,
          })}
          aria-hidden="true"
        >
          <div className="usa-alert__body">
            <p className="usa-alert__text">{localAlert.message}</p>
          </div>
        </div>
      )}

      {processingAlert.active && (
        <div
          className={classNames('usa-alert usa-alert--slim', {
            [`usa-alert--${processingAlert.type}`]: true,
          })}
          aria-hidden="true"
        >
          <div className="usa-alert__body">
            <p className="usa-alert__text">{processingAlert.message}</p>
          </div>
        </div>
      )}

      <form onSubmit={onSubmit}>
        {fileUploadSections.slice(0, num_sections).map((section, index) => (
          <FileUpload
            key={section}
            section={section}
            label={`Section ${index + 1} - ${fileTypeInputValue.toUpperCase()} - ${section}`}
            year={yearInputValue}
            quarter={quarterInputValue}
            fileType={fileTypeInputValue}
            setLocalAlertState={setLocalAlertState}
          />
        ))}

        <div className="buttonContainer margin-y-4">
          <Button
            className="card:margin-y-1"
            type="submit"
            disabled={isSubmitting || uploadedFiles.length === 0}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Data Files'}
          </Button>

          <Button className="cancel" type="button" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </>
  )
}

export default SectionFileUploadForm
