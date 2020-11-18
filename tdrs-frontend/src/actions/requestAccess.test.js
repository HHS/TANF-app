import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  requestAccess,
  PATCH_REQUEST_ACCESS,
  SET_REQUEST_ACCESS,
  SET_REQUEST_ACCESS_ERROR,
  CLEAR_REQUEST_ACCESS,
} from './requestAccess'

describe('actions/requestAccess.js', () => {
  const mockStore = configureStore([thunk])

  it('sends a PATCH request when requestAccess is called', async () => {
    axios.patch = jest.fn().mockResolvedValue({
      data: {
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
    const profileInfo = {
      firstName: 'harry',
      lastName: 'potter',
      stt: { id: 1 },
    }

    const store = mockStore()

    await store.dispatch(requestAccess(profileInfo))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_ACCESS)
    expect(actions[1].type).toBe(SET_REQUEST_ACCESS)
  })

  it('clears the request access state if there is no data returned from the API', async () => {
    axios.patch = jest.fn().mockResolvedValue({})
    const profileInfo = {
      firstName: 'harry',
      lastName: 'potter',
      stt: { id: 1 },
    }

    const store = mockStore()

    await store.dispatch(requestAccess(profileInfo))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_ACCESS)
    expect(actions[1].type).toBe(CLEAR_REQUEST_ACCESS)
  })

  it('dispatches an error to the store if the API errors', async () => {
    axios.patch = jest.fn().mockRejectedValue(new Error('threw an error'))
    const profileInfo = {
      firstName: 'harry',
      lastName: 'potter',
      stt: { id: 1 },
    }

    const store = mockStore()

    await store.dispatch(requestAccess(profileInfo))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_ACCESS)
    expect(actions[1].type).toBe(SET_REQUEST_ACCESS_ERROR)
  })
})
