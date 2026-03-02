import axios from 'axios'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { v4 as uuidv4 } from 'uuid'
import {
  fetchFeatureFlags,
  FETCH_FEATURE_FLAGS,
  SET_FEATURE_FLAGS,
  SET_FEATURE_FLAGS_ERROR,
  CLEAR_FEATURE_FLAGS,
} from './featureFlags'

describe('actions/featureFlags.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches and sets feature flags from api', async () => {
    const mockFlag = { name: 'test-flag', enabled: true, config: {} }
    axios.get.mockImplementationOnce(() =>
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
    expect(actions[2].payload.featureFlags).toStrictEqual([mockFlag])
  })

  it('dispatches an error to the store if the API errors', async () => {
    axios.get.mockImplementationOnce(() =>
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
