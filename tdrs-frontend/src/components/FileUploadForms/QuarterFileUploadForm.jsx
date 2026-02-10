import classNames from 'classnames'
import Button from '../Button'
import FileUpload from '../FileUpload'
import {
  programIntegrityAuditLabels,
  getQuarterFromIndex,
} from '../Reports/utils'
import { useFileUploadForm } from '../../hooks/useFileUploadForm'

const QuarterFileUploadForm = ({ stt }) => {
  // Transform files for Program Integrity Audit submission
  const transformFiles = (uploadedFiles) => {
    return uploadedFiles.map((file) => {
      const index = programIntegrityAuditLabels.indexOf(file.section)
      const quarterCode = getQuarterFromIndex(index)

      return {
        ...file,
        section: 'Active Case Data',
        quarter: quarterCode,
        is_program_audit: true,
      }
    })
  }

  // Format quarters for success message (Q1, Q2, etc.)
  const formatSections = (uploadedFiles) => {
    const uploadedQuarters = uploadedFiles
      ? uploadedFiles
          .map((file) => {
            const index = programIntegrityAuditLabels.indexOf(file.section)
            return index !== -1 ? getQuarterFromIndex(index) : file.section
          })
          .join(', ')
          .split(' ')
      : []

    if (uploadedQuarters.length > 1) {
      uploadedQuarters.splice(uploadedQuarters.length - 1, 0, 'and')
    }

    return uploadedQuarters.join(' ')
  }

  // Generate submit payload for Program Integrity Audit
  const getSubmitPayload = ({
    year,
    formattedSections,
    logger,
    setLocalAlertState,
    stt,
    uploadedFiles,
    user,
    fileType,
  }) => ({
    quarter: null, // Not used for PIA
    year,
    formattedSections,
    logger,
    setLocalAlertState,
    stt,
    uploadedFiles,
    user,
    ssp: false,
    fileType,
  })

  const {
    yearInputValue,
    fileTypeInputValue,
    localAlert,
    processingAlert,
    uploadedFiles,
    isSubmitting,
    alertRef,
    processingAlertRef,
    onSubmit,
    handleCancel,
    setLocalAlertState,
    setProcessingAlertState,
  } = useFileUploadForm({
    stt,
    transformFiles,
    formatSections,
    getSubmitPayload,
  })

  return (
    <>
      {/* Screen-reader announcer */}
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
        {programIntegrityAuditLabels.map((quarterLabel, index) => (
          <FileUpload
            key={quarterLabel}
            section={quarterLabel}
            year={yearInputValue}
            quarter={`Q${index + 1}`}
            fileType={fileTypeInputValue}
            label={quarterLabel}
            setLocalAlertState={setLocalAlertState}
            setProcessingAlertState={setProcessingAlertState}
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

export default QuarterFileUploadForm
