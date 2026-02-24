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
 * @param {Object} options
 * @param {boolean} options.preservePreview - When true, keep the selected file preview visible
 */
export default function createFileInputErrorState(
  input,
  dropTarget,
  { preservePreview = true } = {}
) {
  const classPrefix = 'usa-file-input'
  const filePreviews = dropTarget.querySelector(`.${classPrefix}__preview`)
  const currentPreviewHeading = dropTarget.querySelector(
    `.${classPrefix}__preview-heading`
  )
  const currentErrorMessage = dropTarget.querySelector(
    `.${classPrefix}__accepted-files-message`
  )

  const instructions = dropTarget.querySelector(`.${classPrefix}__instructions`)

  // Remove existing error messages
  if (currentErrorMessage) {
    currentErrorMessage.outerHTML = ''
    dropTarget.classList.remove('has-invalid-file')
    instructions?.classList.remove('display-block')
  }

  // Optionally remove existing previews; by default keep them visible alongside the error state
  if (!preservePreview && filePreviews !== null) {
    if (currentPreviewHeading) {
      currentPreviewHeading.outerHTML = ''
    }
    instructions?.classList.add('display-block')
    filePreviews.parentNode.removeChild(filePreviews)

    Array.prototype.forEach.call(filePreviews, function removeImages(node) {
      node.parentNode.removeChild(node)
    })
  } else if (instructions) {
    instructions.classList.remove('display-block')
  }

  // Only clear the input when explicitly requested
  if (!preservePreview && input) {
    input.value = '' // eslint-disable-line no-param-reassign
  }
  dropTarget.classList.add(`has-invalid-file`)
}
