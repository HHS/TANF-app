/**
 * TODO: Add docstring
 */
const removeFileInputErrorState = () => {
  const errors = document.querySelectorAll('.has-invalid-file')
  for (const error of errors) {
    error?.classList?.remove('has-invalid-file')
  }
}

export default removeFileInputErrorState
