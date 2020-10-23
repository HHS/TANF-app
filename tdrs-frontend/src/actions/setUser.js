import axios from 'axios'

export const SET_USER = 'SET_USER'
export const SET_USER_ERROR = 'SET_USER_ERROR'
export const CLEAR_USER = 'CLEAR_USER'

export const setUser = () => async (dispatch) => {
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/set_profile/`
    const { data } = await axios.patch(URL, {
      withCredentials: true,
    })
    if (data) {
      dispatch({ type: SET_USER, payload: { data } })
    } else {
      dispatch({ type: CLEAR_USER })
    }
  } catch (error) {
    dispatch({ type: SET_USER_ERROR })
  }
}
