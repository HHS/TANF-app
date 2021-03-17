import reducer from './reports'
import { SET_SELECTED_YEAR } from '../actions/reports'

describe('reducers/upload', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      year: 2020,
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
    })
  })
})
