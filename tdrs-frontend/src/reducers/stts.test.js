import reducer from './stts'
import {
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from '../actions/stts'
import { CLEAR_AUTH } from '../actions/auth'

describe('reducers/stts', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      stts: [],
      loading: false,
    })
  })

  it('should handle FETCH_STTS', () => {
    expect(
      reducer(undefined, {
        type: FETCH_STTS,
      })
    ).toEqual({
      stts: [],
      loading: true,
    })
  })

  it('should handle SET_STTS', () => {
    expect(
      reducer(
        {
          stts: [],
          loading: true,
        },
        {
          type: SET_STTS,
          payload: { sttNames: [{ value: 'alabama', label: 'Alabama' }] },
        }
      )
    ).toEqual({
      stts: [{ value: 'alabama', label: 'Alabama' }],
      loading: false,
    })
  })

  it('should handle CLEAR_STTS', () => {
    expect(
      reducer(
        {
          stts: [{ value: 'alabama', label: 'Alabama' }],
          loading: false,
        },
        {
          type: CLEAR_STTS,
        }
      )
    ).toEqual({
      stts: [],
      loading: false,
    })
  })

  it('should handle SET_STTS_ERROR when user logged out', () => {
    expect(
      reducer(undefined, {
        type: SET_STTS_ERROR,
        payload: { error: 'something went wrong' },
      })
    ).toEqual({
      stts: [],
      loading: false,
      error: 'something went wrong',
    })
  })
})
