//This file contains modified versions of code from:
//https://github.com/uswds/uswds/blob/develop/src/js/components/file-input.js
import escapeHtml from '../../utils/escapeHtml'
import languageEncoding from 'detect-file-encoding-and-language'

export const PREFIX = 'usa'

export const PREVIEW_HEADING_CLASS = `${PREFIX}-file-input__preview-heading`
export const PREVIEW_CLASS = `${PREFIX}-file-input__preview`
export const GENERIC_PREVIEW_CLASS_NAME = `${PREFIX}-file-input__preview-image`
export const TARGET_CLASS = `${PREFIX}-file-input__target`

export const GENERIC_PREVIEW_CLASS = `${GENERIC_PREVIEW_CLASS_NAME}--generic`

export const HIDDEN_CLASS = 'display-none'
export const INSTRUCTIONS_CLASS = `${PREFIX}-file-input__instructions`
export const INVALID_FILE_CLASS = 'has-invalid-file'
export const ACCEPTED_FILE_MESSAGE_CLASS = `${PREFIX}-file-input__accepted-files-message`

const SPACER_GIF =
  'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

/**
 * Removes image previews, we want to start with a clean list every time files are added to the file input
 * @param {HTMLElement} dropTarget - target area div that encases the input
 * @param {HTMLElement} instructions - text to inform users to drag or select files
 */
export const removeOldPreviews = (dropTarget, instructions) => {
  const filePreviews = dropTarget.querySelectorAll(`.${PREVIEW_CLASS}`)
  const currentPreviewHeading = dropTarget.querySelector(
    `.${PREVIEW_HEADING_CLASS}`
  )
  const currentErrorMessage = dropTarget.querySelector(
    `.${ACCEPTED_FILE_MESSAGE_CLASS}`
  )

  /**
   * finds the parent of the passed node and removes the child
   * @param {HTMLElement} node
   */
  const removeImages = (node) => {
    node.parentNode.removeChild(node)
  }

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
    Array.prototype.forEach.call(filePreviews, removeImages)
  }
}

export const checkPreviewDependencies = (targetClassName) => {
  const targetInput = document.querySelector(targetClassName)
  const dropTarget = targetInput?.parentElement
  const instructions = dropTarget?.getElementsByClassName(INSTRUCTIONS_CLASS)[0]

  // guard against the case that uswd has not yet rendered this
  if (!dropTarget || !instructions) return { rendered: false }

  return { rendered: true, instructions: instructions, dropTarget: dropTarget }
}

export const getTargetClassName = (formattedSectionName) =>
  `.${TARGET_CLASS} input#${formattedSectionName}`

export const handlePreview = (fileName, targetClassName) => {
  const deps = checkPreviewDependencies(targetClassName)
  if (!deps.rendered) return false

  const dropTarget = deps.dropTarget
  const instructions = deps.instructions

  removeOldPreviews(dropTarget, instructions)

  const filePreviewsHeading = document.createElement('div')
  instructions.insertAdjacentHTML(
    'afterend',
    `<div class="${PREVIEW_CLASS}" aria-hidden="true">
      <img onerror="this.onerror=null;this.src="${SPACER_GIF}"; this.classList.add("${GENERIC_PREVIEW_CLASS}")" src="${SPACER_GIF}" alt="" class="${GENERIC_PREVIEW_CLASS_NAME} ${GENERIC_PREVIEW_CLASS}"/>
      ${escapeHtml(fileName)}
    <div>`
  )

  // Adds heading above file previews
  dropTarget.insertBefore(filePreviewsHeading, instructions)
  filePreviewsHeading.innerHTML = `Selected file <span class="usa-file-input__choose">Change file</span>`

  // Hides null state content and sets preview heading class
  if (filePreviewsHeading) {
    instructions.classList.add(HIDDEN_CLASS)
    filePreviewsHeading.classList.add(PREVIEW_HEADING_CLASS)
  }
  return true
}

// The package author suggests using a minimum of 500 words to determine the encoding. However, datafiles don't have
// "words" so we're using bytes instead to determine the encoding. See: https://www.npmjs.com/package/detect-file-encoding-and-language
const MIN_BYTES = 500

/* istanbul ignore next */
export const tryGetUTF8EncodedFile = async function (fileBytes, file) {
  // Create a small view of the file to determine the encoding.
  const btyesView = new Uint8Array(fileBytes.slice(0, MIN_BYTES))
  const blobView = new Blob([btyesView], { type: 'text/plain' })
  try {
    const fileInfo = await languageEncoding(blobView)
    const bom = btyesView.slice(0, 3)
    const hasBom = bom[0] === 0xef && bom[1] === 0xbb && bom[2] === 0xbf
    if ((fileInfo && fileInfo.encoding !== 'UTF-8') || hasBom) {
      const utf8Encoder = new TextEncoder()
      const decoder = new TextDecoder(fileInfo.encoding)
      const decodedString = decoder.decode(
        hasBom ? fileBytes.slice(3) : fileBytes
      )
      const utf8Bytes = utf8Encoder.encode(decodedString)
      return new File([utf8Bytes], file.name, file.options)
    }
    return file
  } catch (error) {
    // This is a last ditch fallback to ensure consistent functionality and also allows the unit tests to work in the
    // same way they did before this change. When the unit tests (i.e. Node environment) call `languageEncoding` it
    // expects a Buffer/string/URL object. When the browser calls `languageEncoding`, it expects a Blob/File object.
    // There is not a convenient way or universal object to handle both cases. Thus, when the tests run the call to
    // `languageEncoding`, it raises an exception and we return the file as is which is then dispatched as it would
    // have been before this change.
    console.error('Caught error while handling file encoding. Error:', error)
    return file
  }
}

// import SET_SELECTED_YEAR
// import SET_SELECTED_QUARTER

export const checkHeaderFile = async function (
  result,
  file,
  fiscalSelectedYear,
  fiscalSelectedQuarter
) {
  const CalendarToFiscalYearQuarter = (calendarYear, calendarQuarter) => {
    let quarter = parseInt(calendarQuarter)
    let year = parseInt(calendarYear)
    if (quarter === 4) {
      year = year + 1
    }
    quarter = quarter === 4 ? 1 : quarter + 1
    return [year.toString(), quarter.toString()]
  }
  // reads the first line of file formatted as UTF8Encoded
  const decoder = new TextDecoder('utf-8') // Or another encoding if needed
  const textResult = decoder.decode(result)
  const lines = textResult.split('\n')
  const firstLine = lines[0]
  const yearQuarterRegex = '[0-9]{4}[1-4]'
  const yearQuarter = firstLine.match(yearQuarterRegex)
  const fileYear = yearQuarter?.[0]?.slice(0, 4)
  const fileQuarter = yearQuarter?.[0]?.slice(4, 5)
  const [fiscalFileYear, fiscalFileQuarter] = CalendarToFiscalYearQuarter(
    fileYear,
    fileQuarter
  )
  if (
    yearQuarter &&
    (fiscalFileYear !== fiscalSelectedYear ||
      fiscalFileQuarter !== fiscalSelectedQuarter.slice(1, 2))
  ) {
    return [false, fiscalFileYear, fiscalFileQuarter]
  } else {
    return [true, null, null]
  }
}
