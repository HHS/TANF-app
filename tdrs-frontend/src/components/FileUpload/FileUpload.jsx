import React, { useRef } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import fileType from 'file-type/browser'
import { clearError, clearFile, upload } from '../../actions/reports'
import createFileInputErrorState from '../../utils/createFileInputErrorState'

function FileUpload({ section }) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  // The set of uploaded files in our Redux state
  const files = useSelector((state) => state.reports.files)
  const dispatch = useDispatch()

  // e.g. "1 - Active Case Data" => ["1", "Active Case Data"]
  const [sectionNumber, sectionName] = section.split(' - ')

  const currentFile = files.find((file) => sectionName === file.section)

  const formattedSectionName = currentFile.section
    .split(' ')
    .map((word) => word.toLowerCase())
    .join('-')

  const fileName = currentFile?.fileName
  const hasUploadedFile = Boolean(fileName)

  const ariaDescription = hasUploadedFile
    ? `Selected File ${currentFile?.fileName}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  const inputRef = useRef(null)

  const validateAndUploadFile = (event) => {
    const { name } = event.target
    const file = event.target.files[0]

    dispatch(clearError({ section: name }))
    dispatch(clearFile({ section: name }))

    const blob = file.slice(0, 4)

    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    /**
     * Problem:
     *
     * Solution:
     */

    const filereader = new FileReader()

    filereader.onloadend = (evt) => {
      if (!evt.target.error) {
        const uint = new Uint8Array(evt.target.result)
        const bytes = []
        uint.forEach((byte) => {
          bytes.push(byte.toString(16))
        })
        const header = bytes.join('')

        switch (header) {
          // For some reason, fileType.fromBlob won't detect image/png;
          // Account for this by checking for png and some other file signatures manually.
          case '89504e47':
          case '47494638':
          case 'ffd8ffe0':
          case 'ffd8ffe1':
          case 'ffd8ffe2':
          case 'ffd8ffe3':
          case 'ffd8ffe8':
            createFileInputErrorState(input, dropTarget)
            return
          default:
            break
        }

        fileType.fromBlob(blob).then((res) => {
          // res should be undefined for non-binary files
          if (res) {
            createFileInputErrorState(input, dropTarget)
          }
        })

        dispatch(
          upload({
            section: name,
            file,
          })
        )
      }
    }

    filereader.readAsArrayBuffer(blob)
  }

  return (
    <div
      className={`usa-form-group ${
        currentFile.error ? 'usa-form-group--error' : ''
      }`}
    >
      <label className="usa-label text-bold" htmlFor={formattedSectionName}>
        Section {sectionNumber} - {sectionName}
      </label>
      <div>
        {currentFile.error && (
          <div
            className="usa-error-message"
            id={`${formattedSectionName}-error-alert`}
            role="alert"
          >
            {currentFile.error.message}
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
        ref={inputRef}
        onChange={validateAndUploadFile}
        id={formattedSectionName}
        className="usa-file-input"
        type="file"
        name={sectionName}
        aria-describedby={`${formattedSectionName}-file`}
        aria-hidden="false"
        data-errormessage="We can’t process that file format. Please provide a plain text file."
      />
    </div>
  )
}

FileUpload.propTypes = {
  section: PropTypes.string.isRequired,
}

export default FileUpload
