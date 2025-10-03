import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fileInput } from '@uswds/uswds/src/js/components'
import classNames from 'classnames'
import Button from '../Button'
import FileUpload from '../FileUpload'
import { submit } from '../../actions/reports'
import { fileUploadSections } from '../../reducers/reports'
import { useEventLogger } from '../../utils/eventLogger'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useReportsContext } from '../Reports/ReportsContext'

const SectionFileUploadForm = ({ stt }) => {
  const dispatch = useDispatch()
  const logger = useEventLogger()

  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    localAlert,
    setLocalAlertState,
    uploadedFiles,
    setErrorModalVisible,
    handleClear,
    handleOpenFeedbackWidget,
  } = useReportsContext()

  const user = useSelector((state) => state.auth.user)
  const { isSubmitting, executeSubmission } = useFormSubmission()
  const alertRef = useRef(null)

  const num_sections = stt === undefined ? 4 : stt.num_sections

  const uploadedSections = uploadedFiles
    ? uploadedFiles
        .map((file) => fileUploadSections.indexOf(file.section) + 1)
        .join(', ')
        .split(' ')
    : []

  if (uploadedSections.length > 1) {
    uploadedSections.splice(uploadedSections.length - 1, 0, 'and')
  }

  const formattedSections = uploadedSections.join(' ')

  const onSubmit = async (event) => {
    event.preventDefault()

    if (uploadedFiles.length === 0) {
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'No changes have been made to data files',
      })
      return
    }

    try {
      await executeSubmission(() =>
        dispatch(
          submit({
            quarter: quarterInputValue,
            year: yearInputValue,
            formattedSections,
            logger,
            setLocalAlertState,
            stt: stt?.id,
            uploadedFiles,
            user,
            ssp: fileTypeInputValue === 'ssp-moe',
            fileType: fileTypeInputValue,
          })
        )
      )
      handleOpenFeedbackWidget()
    } catch (error) {
      console.error('Error during form submission:', error)
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'An error occurred during submission. Please try again.',
      })
    }
  }

  const handleCancel = () => {
    if (uploadedFiles.length > 0) {
      setErrorModalVisible(true)
    } else {
      handleClear()
    }
  }

  useEffect(() => {
    fileInput.init()
  }, [])

  useEffect(() => {
    if (localAlert.active && alertRef && alertRef.current) {
      alertRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [localAlert, alertRef])

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

export default SectionFileUploadForm
