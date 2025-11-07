import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fileInput } from '@uswds/uswds/src/js/components'
import {
  submit,
  SET_TANF_SUBMISSION_STATUS,
  getTanfSubmissionStatus,
  getAvailableFileList,
} from '../actions/reports'
import { useEventLogger } from '../utils/eventLogger'
import { useFormSubmission } from './useFormSubmission'
import { useReportsContext } from '../components/Reports/ReportsContext'

/**
 * Custom hook that encapsulates shared file upload form logic
 * Used by both QuarterFileUploadForm and SectionFileUploadForm
 *
 * @param {Object} config - Configuration object
 * @param {Object} config.stt - STT object with id
 * @param {Function} config.transformFiles - Function to transform uploaded files before submission
 * @param {Function} config.formatSections - Function to format section names for display
 * @param {Function} config.getSubmitPayload - Function to generate submit action payload
 * @returns {Object} Form state and handlers
 */
export const useFileUploadForm = ({
  stt,
  transformFiles,
  formatSections,
  getSubmitPayload,
}) => {
  const dispatch = useDispatch()
  const logger = useEventLogger()
  const alertRef = useRef(null)

  const {
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    localAlert,
    setLocalAlertState,
    uploadedFiles,
    setErrorModalVisible,
    setModalTriggerSource,
    handleClearAll,
    handleOpenFeedbackWidget,
    startPolling,
    setSelectedSubmissionTab,
  } = useReportsContext()

  const user = useSelector((state) => state.auth.user)
  const { isSubmitting, executeSubmission } = useFormSubmission()

  // Format sections for display in success message
  const formattedSections = formatSections(uploadedFiles)

  const onFileUploadSuccess = (fileIds) => {
    dispatch(
      getAvailableFileList(
        {
          quarter: quarterInputValue,
          year: yearInputValue,
          stt: stt,
          file_type: fileTypeInputValue,
        },
        () => {
          fileIds.forEach((fileId) =>
            startPolling(
              fileId,
              () => getTanfSubmissionStatus(fileId),
              (response) => {
                let summary = response?.data?.summary
                return summary && summary.status && summary.status !== 'Pending'
              },
              (response) => {
                dispatch({
                  type: SET_TANF_SUBMISSION_STATUS,
                  payload: {
                    datafile_id: fileId,
                    datafile: response?.data,
                  },
                })
                setLocalAlertState({
                  active: true,
                  type: 'success',
                  message: 'Parsing complete.',
                })
              },
              (error) => {
                setLocalAlertState({
                  active: true,
                  type: error.type ? error.type : 'error',
                  message: error.message,
                })
              },
              (onError) => {
                onError({
                  message:
                    'Exceeded max number of tries to update submission status.',
                  type: 'warning',
                })
              }
            )
          )
        }
      )
    )
    // setSelectedSubmissionTab(2)
  }

  // Handle form submission
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
      // Transform files if needed (e.g., for Program Audit)
      const filesToSubmit = transformFiles
        ? transformFiles(uploadedFiles)
        : uploadedFiles

      // Get submit payload with all necessary parameters
      const payload = getSubmitPayload({
        quarter: quarterInputValue,
        year: yearInputValue,
        formattedSections,
        logger,
        setLocalAlertState,
        stt: stt?.id,
        uploadedFiles: filesToSubmit,
        user,
        fileType: fileTypeInputValue,
      })

      await executeSubmission(() =>
        dispatch(submit(payload, onFileUploadSuccess))
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

  // Handle cancel button click
  const handleCancel = () => {
    if (uploadedFiles.length > 0) {
      setModalTriggerSource('cancel')
      setErrorModalVisible(true)
    } else {
      handleClearAll()
    }
  }

  // Initialize USWDS file input component
  useEffect(() => {
    fileInput.init()
  }, [])

  // Scroll to alert when it becomes active
  useEffect(() => {
    if (localAlert.active && alertRef && alertRef.current) {
      alertRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [localAlert, alertRef])

  return {
    // Form state
    yearInputValue,
    quarterInputValue,
    fileTypeInputValue,
    localAlert,
    uploadedFiles,
    isSubmitting,
    alertRef,
    formattedSections,

    // Form handlers
    onSubmit,
    handleCancel,

    // Context setters (for FileUpload components)
    setLocalAlertState,
  }
}
