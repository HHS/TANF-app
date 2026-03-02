import { SET_AUTH } from './auth'
import { patch } from '../fetch-instance'
import { logErrorToServer } from '../utils/eventLogger'

export const PATCH_REQUEST_ACCESS = 'PATCH_REQUEST_ACCESS'
export const SET_REQUEST_ACCESS = 'SET_REQUEST_ACCESS'
export const SET_REQUEST_ACCESS_ERROR = 'SET_REQUEST_ACCESS_ERROR'
export const CLEAR_REQUEST_ACCESS = 'CLEAR_REQUEST_ACCESS'

export const requestAccess =
  ({ firstName, lastName, stt, regions, hasFRAAccess }) =>
  async (dispatch) => {
    dispatch({ type: PATCH_REQUEST_ACCESS })
    const URL = `${process.env.REACT_APP_BACKEND_URL}/users/request_access/`
    const user = {
      first_name: firstName,
      last_name: lastName,
      stt: stt?.id,
      regions: regions ? [...regions] : [],
      has_fra_access: hasFRAAccess,
    }
    const { data, ok, error } = await patch(URL, user)

    if (!ok) {
      logErrorToServer(SET_REQUEST_ACCESS_ERROR)
      dispatch({ type: SET_REQUEST_ACCESS_ERROR, payload: { error } })
      return
    }

    if (data) {
      dispatch({ type: SET_REQUEST_ACCESS })
      dispatch({
        type: SET_AUTH,
        payload: { user: data },
      })
    } else {
      dispatch({ type: CLEAR_REQUEST_ACCESS })
    }
  }
