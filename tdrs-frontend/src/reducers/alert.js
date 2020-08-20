import { SET_ALERT, CLEAR_ALERT } from '../actions/alert'

const initialState = {
  show: false,
  heading: '',
  body: null,
  type: '',
}

const alert = (state = initialState, action) => {
  switch (action.type) {
    case SET_ALERT: {
      return { ...state, ...action.alert, show: true }
    }
    case CLEAR_ALERT:
      return initialState
    default:
      return state
  }
}

export default alert
