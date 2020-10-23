import { SET_USER, SET_USER_ERROR, CLEAR_USER } from '../actions/setUser'

const initialState = {
  user: null,
}

const setUser = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_USER: {
      const { data } = payload
      return {
        ...state,
        user: data,
      }
    }
    case SET_USER_ERROR: {
      const { error } = payload
      return {
        ...initialState,
        error,
      }
    }
    case CLEAR_USER:
      return initialState
    default:
      return state
  }
}

export default setUser
