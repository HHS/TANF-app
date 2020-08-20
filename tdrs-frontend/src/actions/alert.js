export const SET_ALERT = 'SET_ALERT'
export const CLEAR_ALERT = 'CLEAR_ALERT'

export const setAlert = (alert) => (dispatch) => {
  return dispatch({ type: SET_ALERT, alert })
}
export const clearAlert = () => (dispatch) => {
  return dispatch({ type: CLEAR_ALERT })
}
