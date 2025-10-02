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
const HEADER_LENGTH = 23 * 4 // Multiply by 4 because some encodings are 4 bytes per char

/* istanbul ignore next */
const checkBom = (bytesView) => {
  // Check for different types of BOMs
  let skipBytes = 0
  const bom = bytesView.slice(0, 4) // Get enough bytes for any BOM

  // UTF-8 BOM: EF BB BF
  const hasUtf8Bom = bom[0] === 0xef && bom[1] === 0xbb && bom[2] === 0xbf
  if (hasUtf8Bom) skipBytes = 3

  // UTF-16 BE BOM: FE FF
  const hasUtf16BeBom = bom[0] === 0xfe && bom[1] === 0xff
  if (hasUtf16BeBom) skipBytes = 2

  // UTF-16 LE BOM: FF FE
  const hasUtf16LeBom = bom[0] === 0xff && bom[1] === 0xfe
  if (hasUtf16LeBom) skipBytes = 2

  // UTF-32 BE BOM: 00 00 FE FF
  const hasUtf32BeBom =
    bom[0] === 0x00 && bom[1] === 0x00 && bom[2] === 0xfe && bom[3] === 0xff
  if (hasUtf32BeBom) skipBytes = 4

  // UTF-32 LE BOM: FF FE 00 00
  const hasUtf32LeBom =
    bom[0] === 0xff && bom[1] === 0xfe && bom[2] === 0x00 && bom[3] === 0x00
  if (hasUtf32LeBom) skipBytes = 4

  const hasBom = skipBytes > 0

  return { hasBom, skipBytes }
}

/* istanbul ignore next */
export const tryGetUTF8EncodedFile = async function (fileBytes, file) {
  // Create a small view of the file to determine the encoding.
  const bytesView = new Uint8Array(fileBytes.slice(0, MIN_BYTES))
  const blobView = new Blob([bytesView])
  try {
    const fileInfo = await languageEncoding(blobView)
    const decoder = new TextDecoder(fileInfo.encoding)
    let retFile = file
    let headerText = decoder.decode(fileBytes.slice(0, HEADER_LENGTH))
    const { hasBom, skipBytes } = checkBom(bytesView)

    if ((fileInfo && fileInfo.encoding !== 'UTF-8') || hasBom) {
      const utf8Encoder = new TextEncoder()
      const newBytes = hasBom ? fileBytes.slice(skipBytes) : fileBytes
      headerText = decoder.decode(newBytes.slice(0, HEADER_LENGTH))
      const decodedString = decoder.decode(newBytes)
      const utf8Bytes = utf8Encoder.encode(decodedString)
      retFile = new File([utf8Bytes], file.name, file.options)
    }

    return { encodedFile: retFile, header: headerText }
  } catch (error) {
    // This is a last ditch fallback to ensure consistent functionality and also allows the unit tests to work in the
    // same way they did before this change. When the unit tests (i.e. Node environment) call `languageEncoding` it
    // expects a Buffer/string/URL object. When the browser calls `languageEncoding`, it expects a Blob/File object.
    // There is not a convenient way or universal object to handle both cases. Thus, when the tests run the call to
    // `languageEncoding`, it raises an exception and we return the file and decode the header as is which is then
    // dispatched as it would have been.
    const decoder = new TextDecoder()
    const header = decoder.decode(bytesView.slice(0, HEADER_LENGTH))
    return { encodedFile: file, header: header }
  }
}

const validateCalendarToFiscalYearQuarter = (
  header,
  selectedFiscalYear,
  selectedFiscalQuarter,
  selectedProgramType
) => {
  const CalendarToFiscalYearQuarter = (calendarYear, calendarQuarter) => {
    let quarter = parseInt(calendarQuarter)
    let year = parseInt(calendarYear)
    if (quarter === 4) {
      year = year + 1
    }
    quarter = quarter === 4 ? 1 : quarter + 1
    return [year.toString(), quarter.toString()]
  }

  const yearQuarterRegex = '[0-9]{4}[1-4]'
  const yearQuarter = header.match(yearQuarterRegex)
  const fileYear = yearQuarter?.[0]?.slice(0, 4)
  const fileQuarter = yearQuarter?.[0]?.slice(4, 5)
  const [fileFiscalYear, fileFiscalQuarter] = CalendarToFiscalYearQuarter(
    fileYear,
    fileQuarter
  )

  let isValid = false
  if (selectedProgramType === 'PRO') {
    // For Program Integrity Audit files, only validate year
    isValid = yearQuarter && fileFiscalYear === selectedFiscalYear
  } else {
    // For TANF/SSP files, validate both year and quarter
    isValid = yearQuarter &&
              fileFiscalYear === selectedFiscalYear &&
              fileFiscalQuarter === selectedFiscalQuarter.slice(1, 2)
  }

  return {
    isValid,
    fileFiscalYear,
    fileFiscalQuarter,
  }
}

const validateProgramType = (header, selectedProgramType) => {
  const progTypeRegex = '(TAN|tan|SSP|ssp)'
  const progType = header.match(progTypeRegex)

  if (!progType) {
    return {
      isValid: false,
      progType: null,
    }
  }

  const fileProgType = progType[0].toUpperCase()

  // Program Integrity Audit (PRO) accepts TANF files
  if (selectedProgramType === 'PRO' && fileProgType === 'TAN') {
    return {
      isValid: true,
      progType: fileProgType,
    }
  }

  // Standard validation: file type must match selected type
  return {
    isValid: fileProgType === selectedProgramType,
    progType: fileProgType,
  }
}

export const validateHeader = async function (
  header,
  selectedFiscalYear,
  selectedFiscalQuarter,
  selectedProgramType
) {
  const calendarFiscalResult = validateCalendarToFiscalYearQuarter(
    header,
    selectedFiscalYear,
    selectedFiscalQuarter,
    selectedProgramType
  )
  const programTypeResult = validateProgramType(header, selectedProgramType)
  return {
    isValid: calendarFiscalResult.isValid && programTypeResult.isValid,
    calendarFiscalResult,
    programTypeResult,
  }
}
