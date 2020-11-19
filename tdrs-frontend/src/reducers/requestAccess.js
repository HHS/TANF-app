import {
  PATCH_REQUEST_ACCESS,
  SET_REQUEST_ACCESS,
  SET_REQUEST_ACCESS_ERROR,
  CLEAR_REQUEST_ACCESS,
} from '../actions/requestAccess'

const initialState = {
  requestAccess: false,
  loading: false,
}

const requestAccess = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case PATCH_REQUEST_ACCESS:
      return { ...state, loading: true }
    case SET_REQUEST_ACCESS:
      return {
        ...state,
        loading: false,
        requestAccess: true,
      }
    case SET_REQUEST_ACCESS_ERROR: {
      const { error } = payload
      return {
        ...initialState,
        error,
      }
    }
    case CLEAR_REQUEST_ACCESS:
      return initialState
    default:
      return state
  }
}

export default requestAccess
