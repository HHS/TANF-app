import React from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { clearError, upload } from '../../actions/reports'

function FileUpload({ section }) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.files)
  const dispatch = useDispatch()

  // e.g. "1 - Active Case Data" => ["1", "Active Case Data"]
  const [sectionNumber, sectionName] = section.split(' - ')

  const file = files.find((currentFile) => sectionName === currentFile.section)

  const formattedSectionName = file.section
    .split(' ')
    .map((word) => word.toLowerCase())
    .join('-')

  const fileName = file?.fileName
  const hasUploadedFile = Boolean(fileName)

  const ariaDescription = hasUploadedFile
    ? `Selected File ${file?.fileName}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  const validateAndUploadFile = ({ target }) => {
    dispatch(clearError({ section: target.name }))
    dispatch(
      upload({
        file: target.files[0],
        section: target.name,
      })
    )
  }

  return (
    <div
      className={`usa-form-group ${file.error ? 'usa-form-group--error' : ''}`}
    >
      <label className="usa-label text-bold" htmlFor={formattedSectionName}>
        Section {sectionNumber} - {sectionName}
      </label>
      <div>
        {file.error && (
          <div
            className="usa-error-message"
            id={`${formattedSectionName}-error-alert`}
            role="alert"
          >
            {file.error.message}
          </div>
        )}
      </div>
      <div
        id={`${formattedSectionName}-file`}
        aria-hidden
        className="display-none"
      >
        {ariaDescription}
      </div>
      <input
        onChange={validateAndUploadFile}
        id={formattedSectionName}
        className="usa-file-input"
        type="file"
        name={sectionName}
        aria-describedby={`${formattedSectionName}-file`}
        aria-hidden="false"
        data-errormessage="We can’t process that file format. Please provide a .txt file."
      />
    </div>
  )
}

FileUpload.propTypes = {
  section: PropTypes.string.isRequired,
}

export default FileUpload
