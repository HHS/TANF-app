import reducer from './requestAccess'
import {
  PATCH_REQUEST_ACCESS,
  SET_REQUEST_ACCESS,
  SET_REQUEST_ACCESS_ERROR,
  CLEAR_REQUEST_ACCESS,
} from '../actions/requestAccess'

describe('reducers/requestAccess', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      requestAccess: false,
      loading: false,
    })
  })

  it('should handle PATCH_REQUEST_ACCESS', () => {
    expect(
      reducer(undefined, {
        type: PATCH_REQUEST_ACCESS,
      })
    ).toEqual({
      loading: true,
      requestAccess: false,
    })
  })

  it('should handle SET_REQUEST_ACCESS', () => {
    expect(
      reducer(
        {
          requestAccess: false,
          loading: true,
        },
        {
          type: SET_REQUEST_ACCESS,
        }
      )
    ).toEqual({
      requestAccess: true,
      loading: false,
    })
  })

  it('should handle CLEAR_REQUEST_ACCESS', () => {
    expect(
      reducer(
        {
          loading: false,
          requestAccess: true,
        },
        {
          type: CLEAR_REQUEST_ACCESS,
        }
      )
    ).toEqual({
      loading: false,
      requestAccess: false,
    })
  })

  it('should handle SET_REQUEST_ACCESS_ERROR', () => {
    expect(
      reducer(
        {
          loading: false,
          requestAccess: true,
        },
        {
          type: SET_REQUEST_ACCESS_ERROR,
          payload: { error: 'something went wrong' },
        }
      )
    ).toEqual({
      loading: false,
      requestAccess: false,
      error: 'something went wrong',
    })
  })
})
