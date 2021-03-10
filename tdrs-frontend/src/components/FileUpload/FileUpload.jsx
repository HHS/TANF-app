import React from 'react'
import PropTypes from 'prop-types'

function FileUpload({ file, section, onUpload }) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  const formattedName = file.section
    .split(' ')
    .map((word) => word.toLowerCase())
    .join('-')

  return (
    <div
      className={`usa-form-group ${file.error ? 'usa-form-group--error' : ''}`}
    >
      <label className="usa-label text-bold" htmlFor={formattedName}>
        Section {section} - {file.section}
      </label>

      <div>
        {file.error && (
          <div
            className="usa-error-message"
            id={`${formattedName}-error-alert`}
            role="alert"
          >
            {file.error.message}
          </div>
        )}
      </div>
      <input
        onChange={(e) => onUpload(e)}
        id={formattedName}
        className="usa-file-input"
        type="file"
        name={file.section}
        aria-describedby={`${formattedName}-specific-hint`}
        accept=".txt"
        data-errormessage="We can’t process that file format. Please provide a .txt file."
      />
    </div>
  )
}

FileUpload.propTypes = {
  file: PropTypes.shape({
    section: PropTypes.string.isRequired,
    file: PropTypes.string,
    error: PropTypes.shape({
      message: PropTypes.string,
    }),
  }).isRequired,
  onUpload: PropTypes.func.isRequired,
  section: PropTypes.string.isRequired,
}

export default FileUpload
