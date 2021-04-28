const PREFIX = 'usa'

const PREVIEW_HEADING_CLASS = `${PREFIX}-file-input__preview-heading`
const PREVIEW_CLASS = `${PREFIX}-file-input__preview`
const GENERIC_PREVIEW_CLASS_NAME = `${PREFIX}-file-input__preview-image`
const ACCEPTED_FILE_MESSAGE_CLASS = `${PREFIX}-file-input__accepted-files-message`
const TARGET_CLASS = `${PREFIX}-file-input__target`

const GENERIC_PREVIEW_CLASS = `${GENERIC_PREVIEW_CLASS_NAME}--generic`

const LOADING_CLASS = 'is-loading'
const INVALID_FILE_CLASS = 'has-invalid-file'
const HIDDEN_CLASS = 'display-none'
const INSTRUCTIONS_CLASS = `${PREFIX}-file-input__instructions`

const SPACER_GIF =
  'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

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

export const getTargetClassName = (formattedSectionName) =>
  `.${TARGET_CLASS} input#${formattedSectionName}`

export const handlePreview = (fileName, targetClassName) => {
  const targetInput = document.querySelector(targetClassName)
  const dropTarget = targetInput?.parentElement

  const instructions = dropTarget?.getElementsByClassName(INSTRUCTIONS_CLASS)[0]
  const filePreviewsHeading = document.createElement('div')

  console.log({
    targetInput,
    dropTarget,
    instructions,
    targetClassName,
    fileName,
  })
  // guard against the case that uswd has not yet rendered this
  if (!dropTarget || !instructions) return false

  // First, get rid of existing previews
  removeOldPreviews(dropTarget, instructions)

  // Iterates through files list and creates previews
  const imageId = makeSafeForID(fileName)

  // Removes loader and displays preview

  const previewImageHTML = `<img id="${imageId}" src="${SPACER_GIF}" alt="" class="${GENERIC_PREVIEW_CLASS_NAME} ${GENERIC_PREVIEW_CLASS}"/>`

  instructions.insertAdjacentHTML(
    'afterend',
    `<div class="${PREVIEW_CLASS}" aria-hidden="true">${previewImageHTML}${fileName}<div>`
  )

  const previewImage = document.getElementById(imageId)
  previewImage.setAttribute(
    'onerror',
    `this.onerror=null;this.src="${SPACER_GIF}"; this.classList.add("${GENERIC_PREVIEW_CLASS}")`
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
