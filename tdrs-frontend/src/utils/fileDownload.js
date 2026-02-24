/**
 * Downloads a blob as a file by creating a temporary anchor element.
 *
 * This utility handles the browser download pattern:
 * 1. Creates a temporary URL for the blob data
 * 2. Creates an invisible anchor element with the download attribute
 * 3. Programmatically clicks it to trigger the browser's download dialog
 * 4. Cleans up the DOM element and revokes the URL to free memory
 *
 * @param {Blob} blob - The blob data to download
 * @param {string} filename - The filename for the downloaded file
 */
export const downloadBlob = (blob, filename) => {
  const url = window.URL.createObjectURL(new Blob([blob]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
