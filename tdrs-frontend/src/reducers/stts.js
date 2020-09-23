import {
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from '../actions/stts'

const initialState = {
  stts: [],
  loading: false,
}

const stts = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case FETCH_STTS:
      return { ...state, loading: true }
    case SET_STTS: {
      const { sttNames } = payload
      return {
        ...state,
        loading: false,
        stts: sttNames,
      }
    }
    case SET_STTS_ERROR: {
      const { error } = payload
      return {
        ...initialState,
        error,
      }
    }
    case CLEAR_STTS:
      return initialState
    default:
      return state
  }
}

export default stts
