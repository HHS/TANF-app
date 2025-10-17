import axios from 'axios'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import { SET_AUTH } from './auth'
import {
  CLEAR_REQUEST_USER_UPDATE,
  PATCH_REQUEST_USER_UPDATE,
  SET_REQUEST_USER_UPDATE,
  SET_REQUEST_USER_UPDATE_ERROR,
  updateUserRequest,
} from './updateUserRequest'

const middlewares = [thunk]
const mockStore = configureStore(middlewares)

describe('updateUserRequest', () => {
  it('dispatches SET_REQUEST_USER_UPDATE with correct user data', async () => {
    const store = mockStore()

    const mockInput = {
      firstName: 'Jane',
      lastName: 'Doe',
      hasFRAAccess: true,
      regions: [1, 3],
    }

    const apiUserResponse = {
      id: 'some-id',
      first_name: 'Jane',
      last_name: 'Doe',
      regions: [1, 3],
      has_fra_access: true,
      pending_requests: 1,
    }
    axios.patch.mockResolvedValue({ data: apiUserResponse })

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions).toEqual([
      { type: PATCH_REQUEST_USER_UPDATE },
      { type: SET_REQUEST_USER_UPDATE },
      { type: SET_AUTH, payload: { user: apiUserResponse } },
    ])
  })

  it('handles missing optional values like regions', async () => {
    const store = mockStore()

    const mockInput = {
      firstName: 'John',
      lastName: 'Smith',
      hasFRAAccess: false,
    }

    const apiUserResponse = {
      id: 'some-id-2',
      first_name: 'John',
      last_name: 'Smith',
      regions: [],
      has_fra_access: false,
      pending_requests: 0,
    }
    axios.patch.mockResolvedValue({ data: apiUserResponse })

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions).toEqual([
      { type: PATCH_REQUEST_USER_UPDATE },
      { type: SET_REQUEST_USER_UPDATE },
      { type: SET_AUTH, payload: { user: apiUserResponse } },
    ])
  })

  it('dispatches an error to the store if the API errors', async () => {
    const store = mockStore()

    const mockInput = {
      firstName: 'John',
      lastName: 'Smith',
      stt: undefined,
      hasFRAAccess: false,
    }

    axios.patch.mockRejectedValue(new Error('threw and error'))

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_USER_UPDATE)
    expect(actions[1].type).toBe(SET_REQUEST_USER_UPDATE_ERROR)
  })

  it('dispatches an error to the store if the API errors', async () => {
    const store = mockStore()

    const mockInput = {
      firstName: 'John',
      lastName: 'Smith',
      stt: undefined,
      hasFRAAccess: false,
    }

    axios.patch.mockResolvedValue({})

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_USER_UPDATE)
    expect(actions[1].type).toBe(CLEAR_REQUEST_USER_UPDATE)
  })
})
