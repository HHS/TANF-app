import {
  FETCH_FEATURE_FLAGS,
  SET_FEATURE_FLAGS,
  SET_FEATURE_FLAGS_ERROR,
  CLEAR_FEATURE_FLAGS,
} from '../actions/featureFlags'

const initialState = {
  loading: false,
  error: null,
  featureFlags: null,
  lastFetched: null,
}

const featureFlags = (state = initialState, action) => {
  const { type, payload = {} } = action

  switch (type) {
    case FETCH_FEATURE_FLAGS:
      return {
        ...state,
        loading: true,
        error: null,
        lastFetched: null,
      }
    case SET_FEATURE_FLAGS: {
      const { featureFlags, lastFetched } = payload
      return {
        ...state,
        loading: false,
        featureFlags,
        lastFetched,
      }
    }
    case SET_FEATURE_FLAGS_ERROR: {
      const { error, lastFetched } = payload
      return {
        ...state,
        loading: false,
        error,
        lastFetched,
      }
    }
    case CLEAR_FEATURE_FLAGS:
      return initialState
    default:
      return state
  }
}

export default featureFlags
