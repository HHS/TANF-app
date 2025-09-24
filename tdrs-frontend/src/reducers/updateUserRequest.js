import {
  SET_REQUEST_USER_UPDATE,
  SET_REQUEST_USER_UPDATE_ERROR,
  CLEAR_REQUEST_USER_UPDATE,
  PATCH_REQUEST_USER_UPDATE,
} from '../actions/updateUserRequest'

const initialState = {
  requestUpdateUser: false,
  loading: false,
}

const updateUserRequest = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case PATCH_REQUEST_USER_UPDATE:
      return { ...state, loading: true }
    case SET_REQUEST_USER_UPDATE:
      return {
        ...state,
        loading: false,
        requestUpdateUser: true,
      }
    case SET_REQUEST_USER_UPDATE_ERROR: {
      const { error } = payload
      return {
        ...initialState,
        error,
      }
    }
    case CLEAR_REQUEST_USER_UPDATE:
      return initialState
    default:
      return state
  }
}

export default updateUserRequest
