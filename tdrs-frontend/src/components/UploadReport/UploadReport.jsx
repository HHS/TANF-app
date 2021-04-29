import React, { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import { fileInput } from 'uswds/src/js/components'

import classNames from 'classnames'
import Button from '../Button'

import FileUpload from '../FileUpload'
import axiosInstance from '../../axios-instance'
import { clearError } from '../../actions/reports'
import { useEventLogger } from '../../utils/eventLogger'

function UploadReport({ handleCancel, header }) {
  // The currently selected year from the reportingYears dropdown
  const selectedYear = useSelector((state) => state.reports.year)

  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.files)
  // The logged in user in our Redux state
  const user = useSelector((state) => state.auth.user)

  const [localAlert, setLocalAlertState] = useState({
    active: false,
    type: null,
    message: null,
  })

  // Ensure newly rendered header is focused,
  // else it won't be read be screen readers.
  const headerRef = useRef(null)
  const dispatch = useDispatch()

  const logger = useEventLogger()

  useEffect(() => {
    headerRef.current.focus()
  }, [])

  const fileUploadSections = [
    'Active Case Data',
    'Closed Case Data',
    'Aggregate Data',
    'Stratum Data',
  ]

  const filteredFiles = files.filter((file) => file.fileName)
  const uploadedSections = filteredFiles
    .map((file) => fileUploadSections.indexOf(file.section) + 1)
    .join(', ')
    .split(' ')

  if (uploadedSections.length > 1) {
    // This is to ensure the trailing 'and': '1, 2, 3' => '1, 2, and 3'
    uploadedSections.splice(uploadedSections.length - 1, 0, 'and')
  }

  const formattedSections = uploadedSections.join(' ')

  const clearErrorState = () => {
    for (const section of fileUploadSections) {
      dispatch(clearError({ section }))
    }

    const errors = document.querySelectorAll('.has-invalid-file')
    for (const error of errors) {
      error?.classList?.remove('has-invalid-file')
    }
  }

  const onSubmit = async (event) => {
    event.preventDefault()

    if (filteredFiles.length === 0) {
      setLocalAlertState({
        active: true,
        type: 'error',
        message: 'No changes have been made to data files',
      })
      return
    }

    const uploadRequests = filteredFiles.map((file) =>
      axiosInstance.post(
        `${process.env.REACT_APP_BACKEND_URL}/reports/`,
        {
          original_filename: file.fileName,
          slug: file.uuid,
          user: user.id,
          year: selectedYear,
          stt: '1',
          quarter: 'Q1',
          section: file.section,
        },
        { withCredentials: true }
      )
    )

    Promise.all(uploadRequests)
      .then((responses) => {
        setLocalAlertState({
          active: true,
          type: 'success',
          message: `Successfully submitted section(s): ${formattedSections} on ${new Date().toDateString()}`,
        })
        clearErrorState()

        // Create LogEntries in Django for each created ReportFile
        logger.alert(`Submitted data file(s)`, {
          files: responses.map((response) => response?.data?.id),
          activity: 'upload',
        })
      })
      .catch((error) => console.error(error))
  }

  const onCancel = () => {
    handleCancel()
    clearErrorState()
  }

  useEffect(() => {
    // `init` for the uswds fileInput must be called on the
    // initial render for it to load properly
    fileInput.init()
  }, [])

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
          <Button className="cancel" type="button" onClick={onCancel}>
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
}

export default UploadReport
