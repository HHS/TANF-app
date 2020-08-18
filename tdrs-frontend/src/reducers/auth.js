import { SET_USER } from '../actions/auth'

const initialState = {
  loading: false,
}

const auth = (state = initialState, action) => {
  switch (action.type) {
    case SET_USER:
      return {
        ...state,
        user: action.user,
      }
    default:
      return state
  }
}

export default auth
