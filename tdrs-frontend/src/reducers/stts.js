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

/**
 * Reduces data on the Redux store for states, tribes and territories.
 *
 * SET_STTS defines states, tribes and territories on the store
 * which is used in the combo box as options to select.
 *
 * SET_STTS_ERROR reverts to the initial state,
 * clears any states, tribes and territories,
 * and sets the error on the store.
 * @param {object} state - The current state of the application
 * or the initial state object.
 * @param {object} action - An object with a type and a payload
 * used in the switch statement to set information on the store.
 */
const stts = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case FETCH_STTS:
      return { ...state, loading: true }
    case SET_STTS: {
      const { data } = payload
      return {
        ...state,
        loading: false,
        stts: data,
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
