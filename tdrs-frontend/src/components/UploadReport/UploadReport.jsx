import React, { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import { fileInput } from 'uswds/src/js/components'
import classNames from 'classnames'
import Button from '../Button'

import FileUpload from '../FileUpload'
import { submit } from '../../actions/reports'
import { useEventLogger } from '../../utils/eventLogger'
import { fileUploadSections } from '../../reducers/reports'

function UploadReport({ handleCancel, header, stt }) {
  // The currently selected year from the reportingYears dropdown
  const selectedYear = useSelector((state) => state.reports.year)
  // The selected quarter in the dropdown tied to our redux `reports` state
  const selectedQuarter = useSelector((state) => state.reports.quarter)
  // The selected File Type value from redux
  const selectedFileType = useSelector((state) => state.reports.fileType)

  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.files)
  // The logged in user in our Redux state
  const user = useSelector((state) => state.auth.user)

  // TODO: Move this to Redux state so we can modify this value outside of
  // this component without having to pass the setter function around
  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })
  const alertRef = useRef(null)

  // Ensure newly rendered header is focused,
  // else it won't be read be screen readers.
  const headerRef = useRef(null)
  const dispatch = useDispatch()

  const logger = useEventLogger()

  useEffect(() => {
    headerRef.current.focus()
  }, [])

  const uploadedFiles = files.filter((file) => file.fileName && !file.id)
  const uploadedSections = uploadedFiles
    .map((file) => fileUploadSections.indexOf(file.section) + 1)
    .join(', ')
    .split(' ')

  if (uploadedSections.length > 1) {
    // This is to ensure the trailing 'and': '1, 2, 3' => '1, 2, and 3'
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

    dispatch(
      submit({
        quarter: selectedQuarter,
        year: selectedYear,
        formattedSections,
        logger,
        setLocalAlertState,
        stt,
        uploadedFiles,
        user,
        ssp: selectedFileType === 'ssp-moe',
      })
    )
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
      <h2
        ref={headerRef}
        className="font-serif-xl margin-top-5 margin-bottom-0 text-normal"
        tabIndex="-1"
      >
        {header}
      </h2>
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
        {fileUploadSections.map((name, index) => (
          <FileUpload
            key={name}
            section={`${index + 1} - ${name}`}
            setLocalAlertState={setLocalAlertState}
          />
        ))}

        <div className="buttonContainer margin-y-4">
          <Button className="card:margin-y-1" type="submit">
            Submit Data Files
          </Button>

          <Button className="cancel" type="button" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </>
  )
}

UploadReport.propTypes = {
  handleCancel: PropTypes.func.isRequired,
  header: PropTypes.string.isRequired,
  stt: PropTypes.number,
}

export default UploadReport
