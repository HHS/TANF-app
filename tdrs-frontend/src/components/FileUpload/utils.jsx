//This file contains modified versions of code from:
//https://github.com/uswds/uswds/blob/develop/src/js/components/file-input.js
export const PREFIX = 'usa'

export const PREVIEW_HEADING_CLASS = `${PREFIX}-file-input__preview-heading`
export const PREVIEW_CLASS = `${PREFIX}-file-input__preview`
export const GENERIC_PREVIEW_CLASS_NAME = `${PREFIX}-file-input__preview-image`
export const TARGET_CLASS = `${PREFIX}-file-input__target`

export const GENERIC_PREVIEW_CLASS = `${GENERIC_PREVIEW_CLASS_NAME}--generic`

export const HIDDEN_CLASS = 'display-none'
export const INSTRUCTIONS_CLASS = `${PREFIX}-file-input__instructions`

const SPACER_GIF =
  'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'

export const getTargetClassName = (formattedSectionName) =>
  `.${TARGET_CLASS} input#${formattedSectionName}`

export const handlePreview = (fileName, targetClassName) => {
  const targetInput = document.querySelector(targetClassName)
  const dropTarget = targetInput?.parentElement

  const instructions = dropTarget?.getElementsByClassName(INSTRUCTIONS_CLASS)[0]
  const filePreviewsHeading = document.createElement('div')

  // guard against the case that uswd has not yet rendered this
  if (!dropTarget || !instructions) return false

  instructions.insertAdjacentHTML(
    'afterend',
    `<div class="${PREVIEW_CLASS}" aria-hidden="true">
      <img onerror="this.onerror=null;this.src="${SPACER_GIF}"; this.classList.add("${GENERIC_PREVIEW_CLASS}")" src="${SPACER_GIF}" alt="" class="${GENERIC_PREVIEW_CLASS_NAME} ${GENERIC_PREVIEW_CLASS}"/>
      ${fileName}
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
