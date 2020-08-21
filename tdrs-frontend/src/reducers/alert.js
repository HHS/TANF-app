import { SET_ALERT, CLEAR_ALERT } from '../actions/alert'

const initialState = {
  show: false,
  heading: '',
  body: null,
  type: '',
}

const alertReducer = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_ALERT: {
      const { alert } = payload
      return { ...state, ...alert, show: true }
    }
    case CLEAR_ALERT:
      return initialState
    default:
      return state
  }
}

export default alertReducer
