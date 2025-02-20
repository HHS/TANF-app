//This file contains modified versions of code from:
//https://github.com/uswds/uswds/blob/develop/src/js/components/file-input.js
import escapeHtml from '../../utils/escapeHtml'

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
