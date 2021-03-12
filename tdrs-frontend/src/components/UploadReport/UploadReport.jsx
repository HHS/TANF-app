import React, { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import PropTypes from 'prop-types'
import { fileInput } from 'uswds/src/js/components'

import Button from '../Button'

import { clearError, upload } from '../../actions/reports'
import FileUpload from '../FileUpload'

function UploadReport({ handleCancel }) {
  // The currently selected year from the reportingYears dropdown
  const selectedYear = useSelector((state) => state.reports.year)

  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.files)
  const getFile = (sectionName) => {
    return files.find((file) => sectionName === file.section)
  }
  const dispatch = useDispatch()

  const uploadFiles = ({ target }) => {
    dispatch(clearError({ section: target.name }))
    dispatch(
      upload({
        file: target.files[0],
        section: target.name,
      })
    )
  }

  useEffect(() => {
    // `init` for the uswds fileInput must be called on the
    // initial render for it to load properly
    fileInput.init()
  }, [])

  return (
    <div aria-live="polite">
      <h2 className="font-serif-xl margin-top-5 margin-bottom-0 text-normal">
        Fiscal Year {selectedYear}
      </h2>
      <form>
        <FileUpload
          file={getFile('Active Case Data')}
          section="1"
          onUpload={uploadFiles}
        />
        <FileUpload
          file={getFile('Closed Case Data')}
          section="2"
          onUpload={uploadFiles}
        />
        <FileUpload
          file={getFile('Aggregate Data')}
          section="3"
          onUpload={uploadFiles}
        />
        <FileUpload
          file={getFile('Stratum Data')}
          section="4"
          onUpload={uploadFiles}
        />
        <div className="buttonContainer margin-y-4">
          <Button className="card:margin-y-1" type="submit">
            Submit Files
          </Button>
          <Button className="cancel" type="button" onClick={handleCancel}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}

UploadReport.propTypes = {
  handleCancel: PropTypes.func.isRequired,
}

export default UploadReport
