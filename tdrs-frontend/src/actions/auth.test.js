import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { fetchAuth, FETCH_AUTH, SET_AUTH } from './auth'

describe('actions/auth.js', () => {
  const mockStore = configureStore([thunk])
  axios.get.mockImplementationOnce(() =>
    Promise.resolve({
      user: { email: 'hi@bye.com' },
    })
  )

  it('fetches a user and sets user info, when the user is authenticated', async () => {
    const store = mockStore()
    await store.dispatch(fetchAuth())
    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_AUTH)
    expect(actions[1].type).toBe(SET_AUTH)
    expect(actions[1].payload.user).toStrictEqual({ email: 'hi@bye.com' })
  })
})
