import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  fetchStts,
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from './stts'

describe('actions/stts.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches a list of stts, when the user is authenticated', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
      })
    )
    const store = mockStore()

    await store.dispatch(fetchStts())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS)
    expect(actions[1].payload.data).toStrictEqual([
      { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
    ])
  })

  it('clears the stt state, if user is not authenticated', async () => {
    axios.get.mockImplementationOnce(() => Promise.resolve({ test: {} }))
    const store = mockStore()

    await store.dispatch(fetchStts())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(CLEAR_STTS)
  })

  it('dispatches an error to the store if the API errors', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.reject(Error({ message: 'something went wrong' }))
    )
    const store = mockStore()

    await store.dispatch(fetchStts())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS_ERROR)
  })
})
