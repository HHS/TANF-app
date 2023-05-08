/* 
Get a list of parse errors for a given file id from the backend using the
`/parsing/parse_errors/{id}` endpoint.
*/
export const getParseErrors = (data_json, filename) => {
  try {
    const blob = b64toBlob(data_json.xls_report, 'blob')
    const blobUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = `${filename}.xlsx`
    document.body.append(link)
    link.click()
    link.remove()
    return link
  } catch (error) {
    console.log(error)
    return Error(error)
  }
}

const b64toBlob = (b64Data, contentType = '', sliceSize = 512) => {
  const byteCharacters = atob(b64Data)
  const byteArrays = []

  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize)

    const byteNumbers = new Array(slice.length)
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i)
    }

    const byteArray = new Uint8Array(byteNumbers)
    byteArrays.push(byteArray)
  }
  const blob = new Blob(byteArrays, { type: contentType })
  return blob
}
