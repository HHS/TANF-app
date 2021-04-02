import React, { useRef } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import fileType from 'file-type/browser'
import { clearError, clearFile, upload } from '../../actions/reports'

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

  const createErrorState = (input, dropTarget) => {
    const classPrefix = 'usa-file-input'
    const filePreviews = dropTarget.querySelector(`.${classPrefix}__preview`)
    const currentPreviewHeading = dropTarget.querySelector(
      `.${classPrefix}__preview-heading`
    )
    const currentErrorMessage = dropTarget.querySelector(
      `.${classPrefix}__accepted-files-message`
    )

    const instructions = dropTarget.querySelector(
      `.${classPrefix}__instructions`
    )

    // Remove the heading above the previews
    if (currentPreviewHeading) {
      currentPreviewHeading.outerHTML = ''
    }

    // Remove existing error messages
    if (currentErrorMessage) {
      currentErrorMessage.outerHTML = ''
      dropTarget.classList.remove('has-invalid-file')
    }

    // Get rid of existing previews if they exist, and show instructions
    if (filePreviews !== null) {
      instructions.classList.remove('display-none')
      filePreviews.parentNode.removeChild(filePreviews)
    }
    Array.prototype.forEach.call(filePreviews, function removeImages(node) {
      node.parentNode.removeChild(node)
    })

    const errorMessage = document.createElement('div')

    input.value = '' // eslint-disable-line no-param-reassign
    dropTarget.insertBefore(errorMessage, input)
    errorMessage.innerHTML = `This is not a valid file type.`
    errorMessage.classList.add(`${classPrefix}__accepted-files-message`)
    dropTarget.classList.add(`has-invalid-file`)
  }

  const validateAndUploadFile = async (event) => {
    const { name } = event.target
    const file = event.target.files[0]

    dispatch(clearError({ section: name }))
    dispatch(clearFile({ section: name }))

    const blob = file.slice(0, 4)

    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode
    console.log({ file })

    /**
     * Problem:
     *
     * Solution:
     */

    const filereader = new FileReader()

    filereader.onloadend = function (evt) {
      if (!evt.target.error) {
        const uint = new Uint8Array(evt.target.result)
        const bytes = []
        uint.forEach((byte) => {
          bytes.push(byte.toString(16))
        })
        const header = bytes.join('').toUpperCase()

        switch (header.toLowerCase()) {
          // For some reason, fileType.fromBlob won't detect image/png;
          // Account for this by checking for png and some other file signatures manually.
          case '89504e47':
          case '47494638':
          case 'ffd8ffe0':
          case 'ffd8ffe1':
          case 'ffd8ffe2':
          case 'ffd8ffe3':
          case 'ffd8ffe8':
            createErrorState(input, dropTarget)
            return
          default:
            break
        }

        fileType.fromBlob(blob).then((res) => {
          // res should be undefined for non-binary files
          if (res) {
            createErrorState(input, dropTarget)
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
