import {
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from '../actions/stts'

const initialState = {
  stts: [
    {
      id: 1,
      type: 'state',
      code: 'AL',
      name: 'Alabama',
    },
    {
      id: 2,
      type: 'state',
      code: 'AK',
      name: 'Alaska',
    },
    {
      id: 140,
      type: 'tribe',
      code: 'AK',
      name: 'Aleutian/Pribilof Islands Association, Inc.',
    },
    {
      id: 52,
      type: 'territory',
      code: 'AS',
      name: 'American Samoa',
    },
    {
      id: 3,
      type: 'state',
      code: 'AZ',
      name: 'Arizona',
    },
  ],
  loading: false,
}

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
