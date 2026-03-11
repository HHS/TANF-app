import { get } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { v4 as uuidv4 } from 'uuid'
import {
  fetchAuth,
  FETCH_AUTH,
  SET_AUTH,
  CLEAR_AUTH,
  SET_AUTH_ERROR,
  SET_DEACTIVATED,
} from './auth'
import { CLEAR_FEATURE_FLAGS, FETCH_FEATURE_FLAGS } from './featureFlags'

jest.mock('../fetch-instance')

describe('actions/auth.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches a user and sets user info, when the user is authenticated', async () => {
    const mockUser = { id: uuidv4(), email: 'hi@bye.com' }
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          user: mockUser,
        },
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_AUTH)
    expect(actions[1].payload.user).toStrictEqual(mockUser)
    expect(actions[2].type).toBe(CLEAR_FEATURE_FLAGS)
    expect(actions[3].type).toBe(FETCH_FEATURE_FLAGS)
  })

  it('clears the auth state, if user is not authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          authenticated: false,
        },
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(CLEAR_AUTH)
    expect(actions[2].type).toBe(CLEAR_FEATURE_FLAGS)
  })

  it('dispatches an error to the store if the API errors', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: false,
        status: 500,
        error: new Error('something went wrong'),
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_AUTH_ERROR)
    expect(actions[2].type).toBe(CLEAR_FEATURE_FLAGS)
  })

  it('clears the auth state and triggers dispatches if the API returns `inactive`', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          authenticated: false,
          inactive: true,
        },
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_DEACTIVATED)
    expect(actions[2].type).toBe(CLEAR_FEATURE_FLAGS)
  })
})
