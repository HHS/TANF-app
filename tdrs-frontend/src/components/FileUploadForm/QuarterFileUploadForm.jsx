import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fileInput } from '@uswds/uswds/src/js/components'
import classNames from 'classnames'
import Button from '../Button'
import FileUpload from '../FileUpload'
import { submit } from '../../actions/reports'
import {
  programIntegrityAuditLabels,
  getQuarterFromIndex,
  PROGRAM_INTEGRITY_SECTION,
} from '../Reports/utils'
import { useEventLogger } from '../../utils/eventLogger'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useReportsContext } from '../Reports/ReportsContext'

const QuarterFileUploadForm = ({ stt }) => {
  const dispatch = useDispatch()
  const logger = useEventLogger()

  const {
    yearInputValue,
    fileTypeInputValue,
    localAlert,
    setLocalAlertState,
    uploadedFiles,
    errorModalVisible,
    setErrorModalVisible,
    handleClear,
    handleOpenFeedbackWidget,
  } = useReportsContext()

  const user = useSelector((state) => state.auth.user)
  const { isSubmitting, executeSubmission } = useFormSubmission()
  const alertRef = useRef(null)

  // Format quarters for success message (Q1, Q2, etc.)
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

  const formattedQuarters = uploadedQuarters.join(' ')

  const onSubmit = async (event) => {
    event.preventDefault()

    console.log('onSubmit called')
    console.log('uploadedFiles.length:', uploadedFiles.length)
    console.log('localAlert before:', localAlert)

    if (uploadedFiles.length === 0) {
      console.log('Setting error alert')
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'No changes have been made to data files',
      })
      console.log('Error alert set, returning early')
      return
    }

    console.log('Proceeding with submission')

    try {
      // Transform files: set section to "Program Audit" and quarter to Q1-Q4
      const filesToSubmit = uploadedFiles.map((file) => {
        const index = programIntegrityAuditLabels.indexOf(file.section)
        const quarterCode = getQuarterFromIndex(index)

        return {
          ...file,
          section: PROGRAM_INTEGRITY_SECTION,
          quarter: quarterCode,
        }
      })

      await executeSubmission(() =>
        dispatch(
          submit({
            quarter: null, // Not used for PIA
            year: yearInputValue,
            formattedSections: formattedQuarters,
            logger,
            setLocalAlertState,
            stt: stt?.id,
            uploadedFiles: filesToSubmit,
            user,
            ssp: false,
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
    console.log('localAlert changed:', localAlert)
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
        {programIntegrityAuditLabels.map((quarterLabel, index) => (
          <FileUpload
            key={quarterLabel}
            section={quarterLabel}
            year={yearInputValue}
            quarter={index + 1}
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
