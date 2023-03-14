import axios from 'axios'
export const SET_PARSE_ERRORS = 'SET_PARSE_ERRORS'
export const SET_PARSE_ERRORS_ERROR = 'SET_PARSE_ERRORS_ERROR'
export const FETCH_PARSE_ERRORS = 'FETCH_PARSE_ERRORS'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

/* 
Get a list of parse errors for a given file id from the backend using the
`/parsing/parse_errors/{id}` endpoint.
*/
export const getParseErrors = () => async (dispatch) => {
  dispatch({
    type: FETCH_PARSE_ERRORS,
  })
  try {
    const response = await axios.get(
      `${process.env.REACT_APP_BACKEND_URL}/parsing/parsing_errors/`,
      {
        responseType: 'json',
      }
    )
    dispatch({
      type: SET_PARSE_ERRORS,
      payload: {
        data: response?.data,
      },
    })
    const data_json = response?.data
    const blob = b64toBlob(data_json.xls_report, 'blob')
    const blobUrl = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = 'results.xlsx'
    document.body.append(link)
    link.click()
    link.remove()
  } catch (error) {
    dispatch({
      type: SET_PARSE_ERRORS_ERROR,
      payload: {
        error,
      },
    })
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
