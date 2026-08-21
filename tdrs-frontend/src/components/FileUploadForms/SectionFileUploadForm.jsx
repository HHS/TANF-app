import React from 'react'
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
    setUploadAlertState,
    setProcessingAlertState,
    stt,
    uploadedFiles,
    user,
    fileType,
  }) => ({
    quarter,
    year,
    formattedSections,
    logger,
    setUploadAlertState,
    setProcessingAlertState,
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
    uploadAlert,
    processingAlert,
    isSubmitting,
    uploadAlertRef,
    processingAlertRef,
    onSubmit,
    handleCancel,
    setUploadAlertState,
    setProcessingAlertState,
  } = useFileUploadForm({
    stt,
    transformFiles,
    formatSections,
    getSubmitPayload,
  })

  return (
    <>
      <form onSubmit={onSubmit}>
        {fileUploadSections.slice(0, num_sections).map((section, index) => (
          <FileUpload
            key={section}
            section={section}
            label={`Section ${index + 1} - ${fileTypeInputValue.toUpperCase()} - ${section}`}
            year={yearInputValue}
            quarter={quarterInputValue}
            fileType={fileTypeInputValue}
            setUploadAlertState={setUploadAlertState}
            setProcessingAlertState={setProcessingAlertState}
          />
        ))}

        <div className="buttonContainer margin-y-4">
          <Button
            className="card:margin-y-1"
            type="submit"
            disabled={isSubmitting}
            data-has-uploaded-files={uploadedFiles.length > 0}
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
