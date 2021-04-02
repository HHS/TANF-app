import { v4 as uuidv4 } from 'uuid'
import axiosInstance from '../axios-instance'

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
    const uuid = uuidv4()
    const resp = await axiosInstance.post(
      // Update with backend URL in env when ready
      '/mock_api/reports/signed_url/',
      {
        file_name: uuid,
        file_type: file.type,
        client_method: 'put_object',
      },
      { withCredentials: true }
    )

    if (resp) {
      const signedURL = resp.data.signed_url
      const options = {
        headers: {
          'Content-Type': file.type,
        },
      }

      await axiosInstance.put(signedURL, file, options)

      dispatch({
        type: SET_FILE,
        payload: {
          fileName: file.name,
          fileType: file.type,
          section,
          uuid,
        },
      })
    } else {
      console.log("THAT DIDN'T WORK")
    }
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
