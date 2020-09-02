import { SET_ALERT, CLEAR_ALERT } from '../actions/alert'

const initialState = {
  show: false,
  heading: '',
  body: null,
  type: '',
}

/**
 * Reduces data onto the Redux store for Alerts
 *
 * SET_ALERT will set 'show' to true,
 * which is what the Notify component depends on
 * to render or hide an alert.
 */
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
