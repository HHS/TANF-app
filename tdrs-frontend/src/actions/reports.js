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

export const clearError = ({ section }) => (dispatch) => {
  dispatch({ type: CLEAR_ERROR, payload: { section } })
}
/**
   Get a list of files that can be downloaded, mainly used to decide if the download button should be present.
*/
export const getAvailableFileList = ({ year, quarter = 'Q1' }) => async (
  dispatch
) => {
  const response = await axios({
    url: `/mock/reports/${year}/${quarter}`,
    method: 'get',
    responseType: 'json',
  })
}

export const download = ({ year, quarter = 'Q1', section }) => async (
  dispatch
) => {
  try {
    dispatch({ type: START_FILE_DOWNLOAD })

    const response = await axios({
      url: `/mock/reports/data-files/${year}/${quarter}/${section}`,
      method: 'get',
      responseType: 'blob',
    })
    const { data } = response

    dispatch({
      type: END_FILE_DOWNLOAD,
      payload: {
        year,
        quarter,
        section,
        data,
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
        section,
      },
    })
  } catch (error) {
    dispatch({ type: SET_FILE_ERROR, payload: { error, section } })
    return false
  }

  return true
}

export const SET_YEAR = 'SET_YEAR'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_YEAR, payload: { year } })
}
