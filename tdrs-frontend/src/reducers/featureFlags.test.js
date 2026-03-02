import reducer from './featureFlags'
import {
  FETCH_FEATURE_FLAGS,
  SET_FEATURE_FLAGS,
  SET_FEATURE_FLAGS_ERROR,
  CLEAR_FEATURE_FLAGS,
} from '../actions/featureFlags'

describe('reducers/featureFlags', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual({
      loading: false,
      error: null,
      flags: null,
      lastFetched: null,
    })
  })

  it('should handle FETCH_FEATURE_FLAGS', () => {
    expect(
      reducer(undefined, {
        type: FETCH_FEATURE_FLAGS,
      })
    ).toEqual({
      loading: true,
      error: null,
      flags: null,
      lastFetched: null,
    })
  })

  it('should handle SET_FEATURE_FLAGS', () => {
    const mockFlag = { name: 'test-feature', enabled: true, config: {} }
    expect(
      reducer(
        {
          loading: true,
          error: null,
          flags: null,
          lastFetched: null,
        },
        {
          type: SET_FEATURE_FLAGS,
          payload: {
            flags: [mockFlag],
            lastFetched: '2020-01-01 5:17am',
          },
        }
      )
    ).toEqual({
      loading: false,
      error: null,
      flags: [mockFlag],
      lastFetched: '2020-01-01 5:17am',
    })
  })

  it('should handle CLEAR_FEATURE_FLAGS', () => {
    const mockFlag = { name: 'test-feature', enabled: true, config: {} }
    expect(
      reducer(
        {
          loading: false,
          error: 'test msg',
          flags: [mockFlag],
          lastFetched: '2020-01-01 5:17am',
        },
        {
          type: CLEAR_FEATURE_FLAGS,
        }
      )
    ).toEqual({
      loading: false,
      error: null,
      flags: null,
      lastFetched: null,
    })
  })

  it('should handle SET_FEATURE_FLAGS_ERROR', () => {
    expect(
      reducer(undefined, {
        type: SET_FEATURE_FLAGS_ERROR,
        payload: {
          error: 'something went wrong',
          lastFetched: '2020-01-01 5:17am',
        },
      })
    ).toEqual({
      loading: false,
      error: 'something went wrong',
      flags: null,
      lastFetched: '2020-01-01 5:17am',
    })
  })
})
