import axios from 'axios'
import { logErrorToServer } from '../utils/eventLogger'
import { SET_AUTH } from './auth'

export const UPDATE_USER_REQUEST_SUCCESS = 'UPDATE_USER_REQUEST_SUCCESS'
export const PATCH_REQUEST_USER_UPDATE = 'PATCH_REQUEST_USER_UPDATE'
export const SET_REQUEST_USER_UPDATE = 'SET_REQUEST_USER_UPDATE'
export const SET_REQUEST_USER_UPDATE_ERROR = 'SET_REQUEST_USER_UPDATE_ERROR'
export const CLEAR_REQUEST_USER_UPDATE = 'CLEAR_REQUEST_USER_UPDATE'

export const updateUserRequest =
  ({ firstName, lastName, stt, regions, hasFRAAccess }) =>
  async (dispatch) => {
    dispatch({ type: PATCH_REQUEST_USER_UPDATE })
    try {
      const URL = `${process.env.REACT_APP_BACKEND_URL}/users/update_profile/`
      const user = {
        first_name: firstName,
        last_name: lastName,
        stt: stt?.id,
        has_fra_access: hasFRAAccess,
        create_change_requests: true,
        // backend requires region value if region key is present.
        // this guards it so the key isn't present if value isn't
        ...(Array.isArray(regions) && regions.length > 0 ? { regions } : {}),
      }
      const { data } = await axios.patch(URL, user, {
        withCredentials: true,
      })

      if (data) {
        dispatch({ type: SET_REQUEST_USER_UPDATE })
        dispatch({
          type: SET_AUTH,
          payload: { user: data },
        })
      } else {
        dispatch({ type: CLEAR_REQUEST_USER_UPDATE })
      }
    } catch (error) {
      logErrorToServer(SET_REQUEST_USER_UPDATE_ERROR)
      dispatch({ type: SET_REQUEST_USER_UPDATE_ERROR, payload: { error } })
    }
  }
