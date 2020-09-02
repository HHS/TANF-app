export const SET_ALERT = 'SET_ALERT'
export const CLEAR_ALERT = 'CLEAR_ALERT'

/**
 * Sets an alert object in the store
 *
 * @param {object} alert - an object that has valid alert properties
 * for the Notify component
 * @param {string} alert.type - The type of the alert:
 * one of ['success', 'info', 'warning', 'error']
 * @param {string} alert.heading - The title of the alert
 * @param {string} body - additional content to include in the alert.
 */
export const setAlert = (alert) => (dispatch) => {
  return dispatch({ type: SET_ALERT, payload: { alert } })
}

/**
 * Clears the alert object from the store
 */
export const clearAlert = () => (dispatch) => {
  return dispatch({ type: CLEAR_ALERT })
}
