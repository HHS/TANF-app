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
      user: {},
    })
  })

  it('should handle PATCH_REQUEST_ACCESS', () => {
    expect(
      reducer(undefined, {
        type: PATCH_REQUEST_ACCESS,
      })
    ).toEqual({
      user: {},
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
          user: {},
        },
        {
          type: SET_REQUEST_ACCESS,
          payload: {
            user: {
              first_name: 'harry',
              last_name: 'potter',
              stt: {
                code: 'AK',
                id: 2,
                name: 'Alaska',
                type: 'state',
              },
            },
          },
        }
      )
    ).toEqual({
      requestAccess: true,
      loading: false,
      user: {
        first_name: 'harry',
        last_name: 'potter',
        stt: {
          code: 'AK',
          id: 2,
          name: 'Alaska',
          type: 'state',
        },
      },
    })
  })

  it('should handle CLEAR_REQUEST_ACCESS', () => {
    expect(
      reducer(
        {
          user: {
            first_name: 'harry',
            last_name: 'potter',
            stt: {
              code: 'AK',
              id: 2,
              name: 'Alaska',
              type: 'state',
            },
          },
          loading: false,
          requestAccess: true,
        },
        {
          type: CLEAR_REQUEST_ACCESS,
        }
      )
    ).toEqual({
      user: {},
      loading: false,
      requestAccess: false,
    })
  })

  it('should handle SET_REQUEST_ACCESS_ERROR', () => {
    expect(
      reducer(
        {
          user: {},
          loading: false,
          requestAccess: true,
        },
        {
          type: SET_REQUEST_ACCESS_ERROR,
          payload: { error: 'something went wrong' },
        }
      )
    ).toEqual({
      user: {},
      loading: false,
      requestAccess: false,
      error: 'something went wrong',
    })
  })
})
