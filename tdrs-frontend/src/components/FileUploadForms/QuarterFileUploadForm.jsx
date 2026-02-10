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
    uploadedFiles,
    isSubmitting,
    alertRef,
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
      {localAlert.active && (
        <div
          ref={alertRef}
          className={classNames('usa-alert usa-alert--slim', {
            [`usa-alert--${localAlert.type}`]: true,
          })}
        >
          <div className="usa-alert__body" role="alert">
            <p className="usa-alert__text">{localAlert.message}</p>
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
          />
        ))}

        <div className="buttonContainer margin-y-4">
          <Button
            className="card:margin-y-1"
            type="submit"
            disabled={isSubmitting}
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
