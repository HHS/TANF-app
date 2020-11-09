// import axios from 'axios'
import { SET_AUTH } from './auth'
import hack from '../utils'

// HACK
//const { axiosInstance } = hack

export const PATCH_REQUEST_ACCESS = 'PATCH_REQUEST_ACCESS'
export const SET_REQUEST_ACCESS = 'SET_REQUEST_ACCESS'
export const SET_REQUEST_ACCESS_ERROR = 'SET_REQUEST_ACCESS_ERROR'
export const CLEAR_REQUEST_ACCESS = 'CLEAR_REQUEST_ACCESS'

export const requestAccess = ({ firstName, lastName, stt: { id } }) => async (
  dispatch
) => {
  dispatch({ type: PATCH_REQUEST_ACCESS })
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/users/set_profile/`
    const user = { first_name: firstName, last_name: lastName, stt: { id } }
    const { data } = await (await hack.axiosInstance).patch(URL, user, {
      withCredentials: true,
    })

    if (data) {
      dispatch({ type: SET_REQUEST_ACCESS })
      dispatch({
        type: SET_AUTH,
        payload: { user: data },
      })
    } else {
      dispatch({ type: CLEAR_REQUEST_ACCESS })
    }
  } catch (error) {
      console.log(error)
    dispatch({ type: SET_REQUEST_ACCESS_ERROR, payload: { error } })
  }
}
