import { patch } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  requestAccess,
  PATCH_REQUEST_ACCESS,
  SET_REQUEST_ACCESS,
  SET_REQUEST_ACCESS_ERROR,
  CLEAR_REQUEST_ACCESS,
} from './requestAccess'

jest.mock('../fetch-instance')

describe('actions/requestAccess.js', () => {
  const mockStore = configureStore([thunk])

  it('sends a PATCH request when requestAccess is called', async () => {
    patch.mockImplementationOnce(() =>
      Promise.resolve({
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
        ok: true,
        status: 200,
        error: null,
      })
    )
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
    patch.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: true,
        status: 200,
        error: null,
      })
    )
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
    patch.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: false,
        status: 500,
        error: new Error('threw an error'),
      })
    )
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
