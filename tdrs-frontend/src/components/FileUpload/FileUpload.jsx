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

const PREVIEW_HEADING_CLASS = `${PREFIX}-file-input__preview-heading`
const INVALID_FILE_ERROR =
  'We can’t process that file format. Please provide a plain text file.'
const PREFIX = ''
const PREVIEW_CLASS = `${PREFIX}-file-input__preview`

const SPACER_GIF =
  'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
const LOADING_CLASS = 'is-loading'
const GENERIC_PREVIEW_CLASS_NAME = `${PREFIX}-file-input__preview-image`
const ACCEPTED_FILE_MESSAGE_CLASS = `${PREFIX}-file-input__accepted-files-message`
const INVALID_FILE_CLASS = 'has-invalid-file'
const HIDDEN_CLASS = 'display-none'
const GENERIC_PREVIEW_CLASS = `${GENERIC_PREVIEW_CLASS_NAME}--generic`

const removeOldPreviews = (dropTarget, instructions) => {
  const filePreviews = dropTarget.querySelectorAll(`.${PREVIEW_CLASS}`)
  const currentPreviewHeading = dropTarget.querySelector(
    `.${PREVIEW_HEADING_CLASS}`
  )
  const currentErrorMessage = dropTarget.querySelector(
    `.${ACCEPTED_FILE_MESSAGE_CLASS}`
  )

  // Remove the heading above the previews
  if (currentPreviewHeading) {
    currentPreviewHeading.outerHTML = ''
  }

  // Remove existing error messages
  if (currentErrorMessage) {
    currentErrorMessage.outerHTML = ''
    dropTarget.classList.remove(INVALID_FILE_CLASS)
  }

  // Get rid of existing previews if they exist, show instructions
  if (filePreviews !== null) {
    if (instructions) {
      instructions.classList.remove(HIDDEN_CLASS)
    }
    Array.prototype.forEach.call(filePreviews, function removeImages(node) {
      node.parentNode.removeChild(node)
    })
  }
}

/**
 * Creates an ID name for each file that strips all invalid characters.
 * @param {string} name - name of the file added to file input
 * @returns {string} same characters as the name with invalid chars removed
 */
const makeSafeForID = (name) => {
  return name.replace(/[^a-z0-9]/g, function replaceName(s) {
    const c = s.charCodeAt(0)
    if (c === 32) return '-'
    if (c >= 65 && c <= 90) return `img_${s.toLowerCase()}`
    return `__${('000', c.toString(16)).slice(-4)}`
  })
}

const handleChange = (e, fileInputEl, instructions, dropTarget) => {
  const fileNames = e.target.files
  const filePreviewsHeading = document.createElement('div')

  // First, get rid of existing previews
  removeOldPreviews(dropTarget, instructions)

  // Iterates through files list and creates previews
  for (let i = 0; i < fileNames.length; i += 1) {
    const reader = new FileReader()
    const fileName = fileNames[i].name

    // Starts with a loading image while preview is created
    reader.onloadstart = function createLoadingImage() {
      const imageId = makeSafeForID(fileName)
      const previewImage = `<img id="${imageId}" src="${SPACER_GIF}" alt="" class="${GENERIC_PREVIEW_CLASS_NAME} ${LOADING_CLASS}"/>`

      instructions.insertAdjacentHTML(
        'afterend',
        `<div class="${PREVIEW_CLASS}" aria-hidden="true">${previewImage}${fileName}<div>`
      )
    }

    // Not all files will be able to generate previews. In case this happens, we provide several types "generic previews" based on the file extension.
    reader.onloadend = function createFilePreview() {
      const imageId = makeSafeForID(fileName)
      const previewImage = document.getElementById(imageId)
      previewImage.setAttribute(
        'onerror',
        `this.onerror=null;this.src="${SPACER_GIF}"; this.classList.add("${GENERIC_PREVIEW_CLASS}")`
      )

      // Removes loader and displays preview
      previewImage.classList.remove(LOADING_CLASS)
      previewImage.src = reader.result
    }

    if (fileNames[i]) {
      reader.readAsDataURL(fileNames[i])
    }

    // Adds heading above file previews, pluralizes if there are multiple
    if (i === 0) {
      dropTarget.insertBefore(filePreviewsHeading, instructions)
      filePreviewsHeading.innerHTML = `Selected file <span class="usa-file-input__choose">Change file</span>`
    } else if (i >= 1) {
      dropTarget.insertBefore(filePreviewsHeading, instructions)
      filePreviewsHeading.innerHTML = `${
        i + 1
      } files selected <span class="usa-file-input__choose">Change files</span>`
    }

    // Hides null state content and sets preview heading class
    if (filePreviewsHeading) {
      instructions.classList.add(HIDDEN_CLASS)
      filePreviewsHeading.classList.add(PREVIEW_HEADING_CLASS)
    }
  }
}

function FileUpload({ section }) {
  // e.g. 'Aggregate Case Data' => 'aggregate-case-data'
  // The set of uploaded files in our Redux state
  const { files, year, quarter, data, canDownload, fileList } = useSelector(
    (state) => state.reports
  )
  const dispatch = useDispatch()

  useEffect(() => {
    if (canDownload) {
      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')

      link.href = url
      link.setAttribute('download', `${year}.${quarter}.${section}.txt`)

      document.body.appendChild(link)

      link.click()

      document.body.removeChild(link)
    }
  }, [canDownload])

  // e.g. "1 - Active Case Data" => ["1", "Active Case Data"]
  const [sectionNumber, sectionName] = section.split(' - ')

  const selectedFile = files.find((file) => sectionName === file.section)

  const formattedSectionName = file.section
    .split(' ')
    .map((s) => s.toLowerCase())
    .join('-')

  const fileName = selectedFile?.fileName
  const hasUploadedFile = Boolean(fileName)

  const ariaDescription = hasUploadedFile
    ? `Selected File ${selectedFile?.fileName}. To change the selected file, click this button.`
    : `Drag file here or choose from folder.`

  const downloadFile = ({ target }) => {
    dispatch(clearError({ section }))
    dispatch(download({ section, year }))
  }
  const inputRef = useRef(null)

  const validateAndUploadFile = (event) => {
    setlocalAlertState({
      active: false,
      type: null,
      message: null,
    })

    const { name } = event.target
    const file = event.target.files[0]

    // Clear existing errors and the current
    // file in the state if the user is re-uploading
    dispatch(clearError({ section: name }))
    dispatch(clearFile({ section: name }))

    // Get the the first 4 bytes of the file with which to check file signatures
    const blob = file.slice(0, 4)

    const input = inputRef.current
    const dropTarget = inputRef.current.parentNode

    const filereader = new FileReader()

    filereader.onloadend = (evt) => {
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
                section: name,
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
          if (res) {
            // reject the file and create an error message
            createFileInputErrorState(input, dropTarget)

            dispatch({
              type: SET_FILE_ERROR,
              payload: {
                error: { message: INVALID_FILE_ERROR },
                section: name,
              },
            })
          }
        })

        // At this point we can reasonably conclude the file is a text file.
        // Add the file to the redux state
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
      <div style={{ marginTop: '25px', marginTop: '20px' }}>
        {fileList?.some((file) => file.section === section) ? (
          <Button className="cancel" type="button" onClick={downloadFile}>
            Download
          </Button>
        ) : null}
      </div>
    </div>
  )
}

FileUpload.propTypes = {
  section: PropTypes.string.isRequired,
  setlocalAlertState: PropTypes.func.isRequired,
}

export default FileUpload
