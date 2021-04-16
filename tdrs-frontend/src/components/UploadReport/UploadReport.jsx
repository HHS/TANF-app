import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import { fileInput } from 'uswds/src/js/components'
import { getAvailableFileList } from '../../actions/reports'

import Button from '../Button'

import FileUpload from '../FileUpload'

function UploadReport({ handleCancel }) {
  // The currently selected year from the reportingYears dropdown
  const selectedYear = useSelector((state) => state.reports.year)

  // Ensure newly rendered header is focused, else it won't be read be screen readers.
  const headerRef = useRef(null)
  const dispatch = useDispatch()

  useEffect(() => {
    headerRef.current.focus()
  }, [])

  useEffect(() => dispatch(getAvailableFileList({ selectedYear })), [
    dispatch,
    getAvailableFileList,
    selectedYear,
  ])

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
      <form>
        <FileUpload section="1 - Active Case Data" />
        <FileUpload section="2 - Closed Case Data" />
        <FileUpload section="3 - Aggregate Data" />
        <FileUpload section="4 - Stratum Data" />

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
