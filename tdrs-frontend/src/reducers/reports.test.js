import reducer from './reports'
import {
  SET_SELECTED_STT,
  SET_SELECTED_YEAR,
  SET_SELECTED_QUARTER,
} from '../actions/reports'

describe('reducers/reports', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      year: '',
      stt: '',
      quarter: '',
    })
  })

  it('should handle "SET_SELECTED_YEAR"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_YEAR,
        payload: {
          year: '2021',
        },
      })
    ).toEqual({
      year: '2021',
      stt: '',
      quarter: '',
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
      year: '',
      stt: 'florida',
      quarter: '',
    })
  })

  it('should handle "SET_SELECTED_QUARTER"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_QUARTER,
        payload: {
          quarter: 'Q1',
        },
      })
    ).toEqual({
      year: '',
      stt: '',
      quarter: 'Q1',
    })
  })
})
