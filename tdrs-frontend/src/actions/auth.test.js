import axios from 'axios'
import thunk from 'redux-thunk'
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

describe('actions/auth.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches a user and sets user info, when the user is authenticated', async () => {
    const mockUser = { id: uuidv4(), email: 'hi@bye.com' }
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          user: mockUser,
        },
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_AUTH)
    expect(actions[1].payload.user).toStrictEqual(mockUser)
  })

  it('clears the auth state, if user is not authenticated', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          authenticated: false,
        },
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(CLEAR_AUTH)
  })

  it('dispatches an error to the store if the API errors', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.reject(Error({ message: 'something went wrong' }))
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_AUTH_ERROR)
  })

  it('clears the auth state and triggers dispatches if the API returns `inactive`', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          authenticated: false,
          inactive: true,
        },
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_DEACTIVATED)
  })
})
