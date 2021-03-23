import reducer from './reports'
import { SET_SELECTED_STT, SET_SELECTED_YEAR } from '../actions/reports'

describe('reducers/reports', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      year: 2020,
      stt: '',
    })
  })

  it('should handle "SET_SELECTED_YEAR"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_YEAR,
        payload: {
          year: 2021,
        },
      })
    ).toEqual({
      year: 2021,
      stt: '',
    })
  })

  it('should handle "SET_SELECTED_STT"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_STT,
        payload: {
          stt: 'florida',
        },
      })
    ).toEqual({
      year: 2020, // 2020 is in the default initial state
      stt: 'florida',
    })
  })
})
