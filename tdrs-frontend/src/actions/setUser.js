import axios from 'axios'

import { SET_AUTH } from './auth'

export const SET_USER = 'SET_USER'
export const SET_USER_ERROR = 'SET_USER_ERROR'
export const CLEAR_USER = 'CLEAR_USER'

export const setUser = ({ firstName, lastName, stt: { id } }) => async (
  dispatch
) => {
  try {
    const URL = `${process.env.REACT_APP_BACKEND_URL}/users/set_profile/`
    const user = { first_name: firstName, last_name: lastName, stt: { id } }
    const { data } = await axios.patch(URL, user, {
      withCredentials: true,
    })
    if (data) {
      dispatch({ type: SET_AUTH, payload: { user: data } })
    } else {
      dispatch({ type: CLEAR_USER })
    }
  } catch (error) {
    dispatch({ type: SET_USER_ERROR, payload: { error } })
  }
}
