import axios from 'axios'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import { SET_AUTH } from './auth'
import {
  PATCH_REQUEST_USER_UPDATE,
  SET_REQUEST_USER_UPDATE,
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
      stt: {
        code: 'AK',
        id: 2,
        name: 'Alaska',
        type: 'state',
      },
      hasFRAAccess: true,
    }

    const apiUserResponse = {
      id: 'some-id',
      first_name: 'Jane',
      last_name: 'Doe',
      stt: 2,
      regions: [],
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

  it('handles missing optional values like regions and stt', async () => {
    const store = mockStore()

    const mockInput = {
      firstName: 'John',
      lastName: 'Smith',
      stt: undefined,
      hasFRAAccess: false,
    }

    const apiUserResponse = {
      id: 'some-id-2',
      first_name: 'John',
      last_name: 'Smith',
      stt: undefined,
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
})
