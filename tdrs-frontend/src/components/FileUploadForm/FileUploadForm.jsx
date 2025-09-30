import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import { fileInput } from '@uswds/uswds/src/js/components'
import classNames from 'classnames'
import Button from '../Button'

import FileUpload from '../FileUpload'
import { submit } from '../../actions/reports'
import { fileUploadSections } from '../../reducers/reports'
import { useEventLogger } from '../../utils/eventLogger'
import { useFormSubmission } from '../../hooks/useFormSubmission'

function FileUploadForm({
  handleCancel,
  stt,
  year,
  quarter,
  fileType,
  openWidget,
  localAlert,
  setLocalAlertState,
}) {
  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.submittedFiles)

  // The logged in user in our Redux state
  const user = useSelector((state) => state.auth.user)

  // The number of sections this stt submits data for and it's ID
  const stt_id = stt?.id
  const num_sections = stt === undefined ? 4 : stt.num_sections

  // Use the form submission hook
  const { isSubmitting, executeSubmission } = useFormSubmission()

  const alertRef = useRef(null)

  const dispatch = useDispatch()

  const logger = useEventLogger()

  const uploadedFiles = files?.filter((file) => file.fileName && !file.id)
  const uploadedSections = uploadedFiles
    ? uploadedFiles
        .map((file) => fileUploadSections.indexOf(file.section) + 1)
        .join(', ')
        .split(' ')
    : []

  if (uploadedSections.length > 1) {
    // This is to ensure the trailing 'and': '1, 2, 3' => '1, 2, and 3'
    uploadedSections.splice(uploadedSections.length - 1, 0, 'and')
  }

  const formattedSections = uploadedSections.join(' ')

  const onSubmit = async (event) => {
    event.preventDefault()

    // Prevent submission if no files have been uploaded
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
            quarter: quarter,
            year: year,
            formattedSections,
            logger,
            setLocalAlertState,
            stt: stt_id,
            uploadedFiles,
            user,
            ssp: fileType === 'ssp-moe',
          })
        )
      )
      openWidget()
    } catch (error) {
      console.error('Error during form submission:', error)
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'An error occurred during submission. Please try again.',
      })
    }
  }

  useEffect(() => {
    // `init` for the uswds fileInput must be called on the
    // initial render for it to load properly
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
        {fileUploadSections.slice(0, num_sections).map((section, index) => {
          return (
            <FileUpload
              key={section}
              section={`${index + 1} - ${section}`}
              year={year}
              quarter={quarter}
              fileType={fileType}
              setLocalAlertState={setLocalAlertState}
            />
          )
        })}

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

FileUploadForm.propTypes = {
  handleCancel: PropTypes.func.isRequired,
  stt: PropTypes.object,
}

export default FileUploadForm
