export const SET_YEAR = 'SET_YEAR'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_YEAR, payload: { year } })
}
