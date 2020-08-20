import { FETCH_AUTH, SET_AUTH, SET_AUTH_ERROR } from '../actions/auth'

const initialState = {
  loading: false,
  authenticated: false,
}

const auth = (state = initialState, action) => {
  switch (action.type) {
    case FETCH_AUTH:
      return { ...state, loading: false }
    case SET_AUTH:
      return {
        ...state,
        authenticated: action.authenticated,
        loading: false,
      }
    case SET_AUTH_ERROR:
      return {
        authenticated: false,
        error: action.error,
        loading: false,
      }
    default:
      return state
  }
}

export default auth
