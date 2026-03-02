import { get } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import {
  fetchFeatureFlags,
  FETCH_FEATURE_FLAGS,
  SET_FEATURE_FLAGS,
  SET_FEATURE_FLAGS_ERROR,
  CLEAR_FEATURE_FLAGS,
} from './featureFlags'

jest.mock('../fetch-instance')

describe('actions/featureFlags.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches and sets feature flags from api', async () => {
    const mockFlag = { name: 'test-flag', enabled: true, config: {} }
    const testDate = Date.now()
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [mockFlag],
      })
    )
    const store = mockStore()

    await store.dispatch(fetchFeatureFlags())

    const actions = store.getActions()
    expect(actions[0].type).toBe(CLEAR_FEATURE_FLAGS)
    expect(actions[1].type).toBe(FETCH_FEATURE_FLAGS)
    expect(actions[2].type).toBe(SET_FEATURE_FLAGS)
    expect(actions[2].payload.flags).toStrictEqual([mockFlag])
    expect(actions[2].payload.lastFetched).toEqual(testDate)
  })

  it('dispatches an error to the store if the API errors', async () => {
    get.mockImplementationOnce(() =>
      Promise.reject(Error({ message: 'something went wrong' }))
    )
    const store = mockStore()

    await store.dispatch(fetchFeatureFlags())

    const actions = store.getActions()
    expect(actions[0].type).toBe(CLEAR_FEATURE_FLAGS)
    expect(actions[1].type).toBe(FETCH_FEATURE_FLAGS)
    expect(actions[2].type).toBe(SET_FEATURE_FLAGS_ERROR)
  })
})
