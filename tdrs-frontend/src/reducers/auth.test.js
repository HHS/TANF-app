import reducer from './auth'
import {
  FETCH_AUTH,
  SET_AUTH,
  SET_AUTH_ERROR,
  CLEAR_AUTH,
  SET_DEACTIVATED,
} from '../actions/auth'

describe('reducers/auth', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      user: null,
      loading: false,
      authenticated: false,
      inactive: false,
    })
  })

  it('should handle FETCH_AUTH', () => {
    expect(
      reducer(undefined, {
        type: FETCH_AUTH,
      })
    ).toEqual({
      user: null,
      loading: true,
      authenticated: false,
      inactive: false,
    })
  })

  it('should handle SET_AUTH', () => {
    expect(
      reducer(
        {
          user: null,
          loading: true,
          authenticated: false,
          inactive: false,
        },
        {
          type: SET_AUTH,
          payload: { user: { email: 'hi@bye.com' } },
        }
      )
    ).toEqual({
      user: { email: 'hi@bye.com' },
      loading: false,
      authenticated: true,
      inactive: false,
    })
  })

  it('should handle CLEAR_AUTH', () => {
    expect(
      reducer(
        {
          user: { email: 'hi@bye.com' },
          loading: false,
          authenticated: true,
          inactive: false,
        },
        {
          type: CLEAR_AUTH,
        }
      )
    ).toEqual({
      user: null,
      loading: false,
      authenticated: false,
      inactive: false,
    })
  })

  it('should handle SET_AUTH_ERROR when user logged out', () => {
    expect(
      reducer(undefined, {
        type: SET_AUTH_ERROR,
        payload: { error: 'something went wrong' },
      })
    ).toEqual({
      user: null,
      loading: false,
      authenticated: false,
      error: 'something went wrong',
      inactive: false,
    })
  })

  it('should handle SET_AUTH_ERROR when user logged in', () => {
    expect(
      reducer(
        {
          user: { email: 'hi@bye.com' },
          loading: false,
          authenticated: true,
          inactive: false,
        },
        {
          type: SET_AUTH_ERROR,
          payload: { error: 'something went wrong' },
        }
      )
    ).toEqual({
      user: null,
      loading: false,
      authenticated: false,
      error: 'something went wrong',
      inactive: false,
    })
  })

  it('should handle SET_DEACTIVATED', () => {
    expect(
      reducer(
        {
          user: { email: 'hi@bye.com' },
          loading: false,
          authenticated: true,
          inactive: false,
        },
        {
          type: SET_DEACTIVATED,
        }
      )
    ).toEqual({
      user: null,
      loading: false,
      authenticated: false,
      inactive: true,
    })
  })
})
