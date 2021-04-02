import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import { fileInput } from 'uswds/src/js/components'

import Button from '../Button'

import FileUpload from '../FileUpload'
import axiosInstance from '../../axios-instance'
import { setAlert } from '../../actions/alert'
import { ALERT_SUCCESS } from '../Alert'

function UploadReport({ handleCancel }) {
  // The currently selected year from the reportingYears dropdown
  const selectedYear = useSelector((state) => state.reports.year)

  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.files)
  const user = useSelector((state) => state.auth.user)

  const dispatch = useDispatch()

  // Ensure newly rendered header is focused, else it won't be read be screen readers.
  const headerRef = useRef(null)

  useEffect(() => {
    headerRef.current.focus()
  }, [])

  const fileUploadSections = [
    'Active Case Data',
    'Closed Case Data',
    'Aggregate Data',
    'Stratum Data',
  ]

  const onSubmit = async (event) => {
    event.preventDefault()
    const filteredFiles = files.filter((file) => file.fileName)

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

    const uploadedSections = filteredFiles
      .map((file) => fileUploadSections.indexOf(file.section) + 1)
      .join(', ')
      .split(' ')

    if (uploadedSections.length > 1) {
      // This is to ensure the trailing 'and': '1, 2, 3' => '1, 2, and 3'
      uploadedSections.splice(uploadedSections.length - 1, 0, 'and')
    }

    const formattedSections = uploadedSections.join(' ')

    Promise.all(uploadRequests)
      .then(() =>
        dispatch(
          setAlert({
            heading: `Successfully submitted sections ${formattedSections} on ${new Date().toDateString()}`,
            type: ALERT_SUCCESS,
          })
        )
      )
      .catch((error) => console.error(error))
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
        Fiscal Year {selectedYear}
      </h2>
      <form onSubmit={onSubmit}>
        {fileUploadSections.map((name, index) => (
          <FileUpload key={name} section={`${index + 1} - ${name}`} />
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
}

export default UploadReport
