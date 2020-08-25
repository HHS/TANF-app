import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import {
  fetchAuth,
  FETCH_AUTH,
  SET_AUTH,
  CLEAR_AUTH,
  SET_AUTH_ERROR,
} from './auth'

describe('actions/auth.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches a user and sets user info, when the user is authenticated', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        user: { email: 'hi@bye.com' },
      })
    )
    const store = mockStore()

    await store.dispatch(fetchAuth())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_AUTH)
    expect(actions[1].payload.user).toStrictEqual({ email: 'hi@bye.com' })
  })

  it('clears the auth state, if user is not authenticated', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        authenticated: false,
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
})
