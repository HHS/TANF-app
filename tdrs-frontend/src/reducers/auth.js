import { FETCH_AUTH, SET_AUTH, SET_AUTH_ERROR } from '../actions/auth'

const initialState = {
  loading: false,
  authenticated: false,
}

const auth = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case FETCH_AUTH:
      return { ...state, loading: true }
    case SET_AUTH: {
      const { authenticated, user } = payload
      return {
        ...state,
        loading: false,
        authenticated,
        user,
      }
    }
    case SET_AUTH_ERROR: {
      const { error } = payload
      return {
        authenticated: false,
        error,
        loading: false,
      }
    }
    default:
      return state
  }
}

export default auth
