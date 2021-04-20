import { logErrorToServer } from '../utils/eventLogger'

import { v4 as uuidv4 } from 'uuid'

export const SET_FILE = 'SET_FILE'
export const CLEAR_FILE = 'CLEAR_FILE'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const CLEAR_ERROR = 'CLEAR_ERROR'

export const clearFile = ({ section }) => (dispatch) => {
  dispatch({ type: CLEAR_FILE, payload: { section } })
}

export const clearError = ({ section }) => (dispatch) => {
  dispatch({ type: CLEAR_ERROR, payload: { section } })
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
    logErrorToServer(SET_FILE_ERROR)
    dispatch({ type: SET_FILE_ERROR, payload: { error, section } })
    return false
  }

  return true
}

export const SET_YEAR = 'SET_YEAR'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_YEAR, payload: { year } })
}
