export const SET_SELECTED_YEAR = 'SET_SELECTED_YEAR'
export const SET_SELECTED_STT = 'SET_SELECTED_STT'

export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_SELECTED_YEAR, payload: { year } })
}

export const setStt = (stt) => (dispatch) => {
  dispatch({ type: SET_SELECTED_STT, payload: { stt } })
}
