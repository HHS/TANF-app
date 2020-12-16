import { SET_YEAR } from '../actions/upload'

const initialState = {
  year: 2020,
}

const upload = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_YEAR: {
      const { year } = payload
      return { ...state, year }
    }
    default:
      return state
  }
}

export default upload
