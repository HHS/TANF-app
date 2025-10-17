import reducer from './updateUserRequest'
import {
  PATCH_REQUEST_USER_UPDATE,
  SET_REQUEST_USER_UPDATE,
  SET_REQUEST_USER_UPDATE_ERROR,
  CLEAR_REQUEST_USER_UPDATE,
} from '../actions/updateUserRequest'

describe('reducers/updateUserRequest', () => {
  it('returns the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      requestUpdateUser: false,
      loading: false,
    })
  })

  it('handles PATCH_REQUEST_USER_UPDATE', () => {
    expect(
      reducer(undefined, {
        type: PATCH_REQUEST_USER_UPDATE,
      })
    ).toEqual({
      requestUpdateUser: false,
      loading: true,
    })
  })

  it('handles SET_REQUEST_USER_UPDATE', () => {
    expect(
      reducer(
        { requestUpdateUser: false, loading: true },
        { type: SET_REQUEST_USER_UPDATE }
      )
    ).toEqual({
      requestUpdateUser: true,
      loading: false,
    })
  })

  it('handles CLEAR_REQUEST_USER_UPDATE', () => {
    expect(
      reducer(
        { requestUpdateUser: true, loading: false },
        { type: CLEAR_REQUEST_USER_UPDATE }
      )
    ).toEqual({
      requestUpdateUser: false,
      loading: false,
    })
  })

  it('handles SET_REQUEST_USER_UPDATE_ERROR', () => {
    expect(
      reducer(
        { requestUpdateUser: true, loading: false },
        {
          type: SET_REQUEST_USER_UPDATE_ERROR,
          payload: { error: 'something went wrong' },
        }
      )
    ).toEqual({
      requestUpdateUser: false,
      loading: false,
      error: 'something went wrong',
    })
  })
})
