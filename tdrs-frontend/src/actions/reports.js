import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'

export const SET_FILE = 'SET_FILE'
export const CLEAR_FILE = 'CLEAR_FILE'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const CLEAR_ERROR = 'CLEAR_ERROR'

export const START_FILE_DOWNLOAD = 'START_FILE_DOWNLOAD'
export const END_FILE_DOWNLOAD = 'END_FILE_DOWNLOAD'
export const FILE_DOWNLOAD_ERROR = 'FILE_DOWNLOAD_ERROR'

export const FETCH_FILE_LIST = 'FETCH_FILE_LIST'
export const SET_FILE_LIST = 'SET_FILE_LIST'
export const FETCH_FILE_LIST_ERROR = 'FETCH_FILE_LIST_ERROR'
export const DOWNLOAD_DIALOG_OPEN = 'DOWNLOAD_DIALOG_OPEN'

export const clearFile = ({ section }) => (dispatch) => {
  dispatch({ type: CLEAR_FILE, payload: { section } })
}

export const clearError = ({ section }) => (dispatch) => {
  dispatch({ type: CLEAR_ERROR, payload: { section } })
}
/**
   Get a list of files that can be downloaded, mainly used to decide if the download button should be present.
*/
export const getAvailableFileList = ({ year, quarter = 'Q1' }) => async (
  dispatch
) => {
  dispatch({
    type: FETCH_FILE_LIST,
  })
  try {
    const response = await axios({
      url: `/mock_api/reports/${year}/${quarter}`,
      method: 'get',
      responseType: 'json',
    })
    dispatch({
      type: SET_FILE_LIST,
      payload: {
        data: response.data,
      },
    })
  } catch (error) {
    dispatch({
      type: FETCH_FILE_LIST_ERROR,
    })
  }
}

export const download = ({ year, quarter = 'Q1', section }) => async (
  dispatch
) => {
  try {
    dispatch({ type: START_FILE_DOWNLOAD })

    const response = await axios({
      url: `/mock_api/reports/data-files/${year}/${quarter}/${section}`,
      method: 'get',
      responseType: 'blob',
    })
    const { data } = response

    dispatch({
      type: END_FILE_DOWNLOAD,
      payload: {
        data,
        year,
        quarter,
        section,
      },
    })
  } catch (error) {
    dispatch({
      type: FILE_DOWNLOAD_ERROR,
      payload: { error, year, quarter, section },
    })
    return false
  }
  return true
}

// Main Redux action to add files to the state
export const upload = ({ file, section }) => async (dispatch) => {
  try {
    dispatch({
      type: SET_FILE,
      payload: {
        fileName: file.name,
        fileType: file.type,
        section,
        uuid: uuidv4(),
      },
    })
  } catch (error) {
    dispatch({
      type: SET_FILE_ERROR,
      payload: { error: Error({ message: 'something went wrong' }), section },
    })
    return false
  }

  return true
}

export const SET_SELECTED_STT = 'SET_SELECTED_STT'
export const SET_SELECTED_YEAR = 'SET_SELECTED_YEAR'

export const setStt = (stt) => (dispatch) => {
  dispatch({ type: SET_SELECTED_STT, payload: { stt } })
}
export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_SELECTED_YEAR, payload: { year } })
}

export const triggerDownloadDialog = ({ year, quarter, section, data }) => (
  dispatch
) => {
  const url = window.URL.createObjectURL(new Blob([data]))
  const link = document.createElement('a')

  link.href = url
  link.setAttribute('download', `${year}.${quarter}.${section}.txt`)

  document.body.appendChild(link)

  link.click()

  document.body.removeChild(link)
  dispatch({ type: DOWNLOAD_DIALOG_OPEN })
}
