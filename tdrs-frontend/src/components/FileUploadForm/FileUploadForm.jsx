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

<<<<<<<< HEAD:tdrs-frontend/src/components/FileUploadForms/SectionFileUploadForm.jsx
const SectionFileUploadForm = ({ stt }) => {
========
function FileUploadForm({ handleCancel, stt, openWidget }) {
  // The currently selected year from the reportingYears dropdown
  const selectedYear = useSelector((state) => state.reports.year)
  // The selected quarter in the dropdown tied to our redux `reports` state
  const selectedQuarter = useSelector((state) => state.reports.quarter)
  // The selected File Type value from redux
  const selectedFileType = useSelector((state) => state.reports.fileType)

  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.submittedFiles)

  // The logged in user in our Redux state
  const user = useSelector((state) => state.auth.user)

  // The number of sections this stt submits data for and it's ID
  const stt_id = stt?.id
  const num_sections = stt === undefined ? 4 : stt.num_sections

  // TODO: Move this to Redux state so we can modify this value outside of
  // this component without having to pass the setter function around
  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

  // Use the form submission hook
  const { isSubmitting, executeSubmission } = useFormSubmission()

  const alertRef = useRef(null)

>>>>>>>> f14008915 (- Use radio component on Reports page):tdrs-frontend/src/components/FileUploadForm/FileUploadForm.jsx
  const dispatch = useDispatch()
  const logger = useEventLogger()

  const {
    yearInputValue,
    quarterInputValue,
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
            label={`Section ${index + 1} ${fileTypeInputValue.toUpperCase()} - ${section}`}
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

<<<<<<<< HEAD:tdrs-frontend/src/components/FileUploadForms/SectionFileUploadForm.jsx
export default SectionFileUploadForm
========
FileUploadForm.propTypes = {
  handleCancel: PropTypes.func.isRequired,
  stt: PropTypes.object,
}

export default FileUploadForm
>>>>>>>> f14008915 (- Use radio component on Reports page):tdrs-frontend/src/components/FileUploadForm/FileUploadForm.jsx
