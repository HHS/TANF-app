/**
 * This utility function is mainly used to manually trigger the respective
 * error classes and cleanup the markup around the USWDS file input
 * component used in FileUpload.jsx
 *
 * This mostly is copied from file-input.js in USWDS with some conveniences
 * for our use case.
 *
 * @param {HTMLElement} input
 * @param {HTMLElement} dropTarget
 */
export default function createFileInputErrorState(input, dropTarget) {
  const classPrefix = 'usa-file-input'
  const filePreviews = dropTarget.querySelector(`.${classPrefix}__preview`)
  const currentPreviewHeading = dropTarget.querySelector(
    `.${classPrefix}__preview-heading`
  )
  const currentErrorMessage = dropTarget.querySelector(
    `.${classPrefix}__accepted-files-message`
  )

  const instructions = dropTarget.querySelector(`.${classPrefix}__instructions`)

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

  input.value = '' // eslint-disable-line no-param-reassign
  dropTarget.classList.add(`has-invalid-file`)
}
