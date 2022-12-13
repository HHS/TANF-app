import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import fileType from 'file-type/browser'

import {
  clearError,
  clearFile,
  SET_FILE_ERROR,
  upload,
  download,
} from '../../actions/reports'
import Button from '../Button'
import createFileInputErrorState from '../../utils/createFileInputErrorState'
import { handlePreview, getTargetClassName } from './utils'

const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'

function FileUpload({ section, setLocalAlertState }) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  // The set of uploaded files in our Redux state
  const { files } = useSelector((state) => state.reports)

  const dispatch = useDispatch()

  // e.g. "1 - Active Case Data" => ["1", "Active Case Data"]
  const [sectionNumber, sectionName] = section.split(' - ')

  const hasFile = files?.some(
    (file) => file.section.includes(sectionName) && file.uuid
  )

  const selectedFile = files.find((file) => file.section.includes(sectionName))

  const formattedSectionName = selectedFile.section
    .split(' ')
    .map((word) => word.toLowerCase())
    .join('-')

  const targetClassName = getTargetClassName(formattedSectionName)

  const fileName = selectedFile?.fileName || 'report.txt'
  const hasUploadedFile = Boolean(fileName)

  const ariaDescription = hasUploadedFile
    ? `Selected File ${selectedFile?.fileName}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  useEffect(() => {
    const trySettingPreview = () => {
      const previewState = handlePreview(fileName, targetClassName)
      if (!previewState) {
        setTimeout(trySettingPreview, 100)
      }
    }
    if (hasFile) trySettingPreview()
  }, [hasFile, fileName, targetClassName])

  const downloadFile = ({ target }) => {
    dispatch(clearError({ section: sectionName }))
    dispatch(download(selectedFile))
  }
  const inputRef = useRef(null)

  const validateAndUploadFile = (event) => {
    setLocalAlertState({
      active: false,
      type: null,
      message: null,
    })

    const { name: section } = event.target
    const file = event.target.files[0]

    // Clear existing errors and the current
    // file in the state if the user is re-uploading
    dispatch(clearError({ section }))
    dispatch(clearFile({ section }))

    // Get the the first 4 bytes of the file with which to check file signatures
    const blob = file.slice(0, 4)

    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    const filereader = new FileReader()

    filereader.onloadend = (evt) => {
      /* istanbul ignore next */
      if (!evt.target.error) {
        // Read in the file blob "headers: and create a hex string signature
        const uint = new Uint8Array(evt.target.result)
        const bytes = []
        uint.forEach((byte) => {
          bytes.push(byte.toString(16))
        })
        const header = bytes.join('')

        switch (header) {
          // For some reason, fileType.fromBlob won't detect image/png;
          // Account for this by checking for png and some other
          // file signatures manually. https://stackoverflow.com/a/55136384/7678576
          case '89504e47': // image/png
          case '47494638': // image/gif
          case 'ffd8ffe0': // all the rest are image/jpeg
          case 'ffd8ffe1':
          case 'ffd8ffe2':
          case 'ffd8ffe3':
          case 'ffd8ffe8':
            // reject the file and create an error message
            createFileInputErrorState(input, dropTarget)

            dispatch({
              type: SET_FILE_ERROR,
              payload: {
                error: { message: INVALID_FILE_ERROR },
                section,
              },
            })
            return
          default:
            break
        }

        // file-type should detect and return values for most other
        // known binary files
        fileType.fromBlob(blob).then((res) => {
          // res should be undefined for non-binary files
          /* istanbul ignore next */
          if (res) {
            // reject the file and create an error message
            createFileInputErrorState(input, dropTarget)

            dispatch({
              type: SET_FILE_ERROR,
              payload: {
                error: { message: INVALID_FILE_ERROR },
                section,
              },
            })
          }
        })

        // At this point we can reasonably conclude the file is a text file.
        // Add the file to the redux state
        dispatch(
          upload({
            section,
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
        selectedFile.error ? 'usa-form-group--error' : ''
      }`}
    >
      <label className="usa-label text-bold" htmlFor={formattedSectionName}>
        Section {sectionNumber} - {sectionName}
      </label>
      <div>
        {selectedFile.error && (
          <div
            className="usa-error-message"
            id={`${formattedSectionName}-error-alert`}
            role="alert"
          >
            {selectedFile.error.message}
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
        data-errormessage={INVALID_FILE_ERROR}
      />
      <div style={{ marginTop: '25px' }}>
        {hasFile && selectedFile?.id ? (
          <Button
            className="tanf-file-download-btn"
            type="button"
            onClick={downloadFile}
          >
            Download Section {sectionNumber}
          </Button>
        ) : null}
      </div>
    </div>
  )
}

FileUpload.propTypes = {
  section: PropTypes.string.isRequired,
  setLocalAlertState: PropTypes.func.isRequired,
}

export default FileUpload
