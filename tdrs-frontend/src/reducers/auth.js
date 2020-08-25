import {
  FETCH_AUTH,
  SET_AUTH,
  SET_AUTH_ERROR,
  CLEAR_AUTH,
} from '../actions/auth'

const initialState = {
  user: null,
  loading: false,
  authenticated: false,
}

const auth = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case FETCH_AUTH:
      return { ...state, loading: true }
    case SET_AUTH: {
      const { user } = payload
      return {
        ...state,
        loading: false,
        authenticated: true,
        user,
      }
    }
    case SET_AUTH_ERROR: {
      const { error } = payload
      return {
        ...initialState,
        error,
      }
    }
    case CLEAR_AUTH:
      return initialState
    default:
      return state
  }
}

export default auth
