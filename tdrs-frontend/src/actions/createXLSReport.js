/* 
Get a list of parse errors for a given file id from the backend using the
`/parsing/parse_errors/{id}` endpoint.
*/
export const getParseErrors = (data_json, filename) => {
  try {
    const blobUrl = URL.createObjectURL(new Blob([data_json]))
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
