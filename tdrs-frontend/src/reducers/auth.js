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

/**
 * Reduces data onto the Redux store for Authentication
 *
 * SET_AUTH defines `authenticated: true` on the store
 * which is used through the app to determine if user is logged in
 *
 * SET_AUTH_ERROR reverts to the initial state,
 * clears any authenticated state),
 * and sets the error on the store
 */
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
