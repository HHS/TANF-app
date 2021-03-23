import {
  SET_SELECTED_STT,
  SET_SELECTED_YEAR,
  SET_SELECTED_QUARTER,
} from '../actions/reports'

const initialState = {
  year: '',
  stt: '',
  quarter: '',
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
    case SET_SELECTED_QUARTER: {
      const { quarter } = payload
      return { ...state, quarter }
    }
    default:
      return state
  }
}

export default reports
