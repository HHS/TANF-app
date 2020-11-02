import reducer from './sttList'
import {
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from '../actions/sttList'

describe('reducers/stts', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      sttList: [],
      loading: false,
    })
  })

  it('should handle FETCH_STTS', () => {
    expect(
      reducer(undefined, {
        type: FETCH_STTS,
      })
    ).toEqual({
      sttList: [],
      loading: true,
    })
  })

  it('should handle SET_STTS', () => {
    expect(
      reducer(
        {
          sttList: [],
          loading: true,
        },
        {
          type: SET_STTS,
          payload: {
            data: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
          },
        }
      )
    ).toEqual({
      sttList: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
      loading: false,
    })
  })

  it('should handle CLEAR_STTS', () => {
    expect(
      reducer(
        {
          sttList: [{ value: 'alabama', label: 'Alabama' }],
          loading: false,
        },
        {
          type: CLEAR_STTS,
        }
      )
    ).toEqual({
      sttList: [],
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
      sttList: [],
      loading: false,
      error: 'something went wrong',
    })
  })
})
