import { SET_SELECTED_STT, SET_SELECTED_YEAR } from '../actions/reports'

const initialState = {
  year: '',
  stt: '',
}

/**
 * These states define the selected entities in the Reports page
 */
const reports = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_SELECTED_YEAR: {
      const { year } = payload
      return { ...state, year }
    }
    case SET_SELECTED_STT: {
      const { stt } = payload
      return { ...state, stt }
    }
    default:
      return state
  }
}

export default reports
