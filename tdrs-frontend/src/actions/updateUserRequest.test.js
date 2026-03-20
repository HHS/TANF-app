import { patch } from '../fetch-instance'
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

jest.mock('../fetch-instance')

const middlewares = [thunk]
const mockStore = configureStore(middlewares)

describe('updateUserRequest', () => {
  it('dispatches SET_REQUEST_USER_UPDATE with correct user data', async () => {
    const existingUser = {
      id: 'some-id',
      first_name: 'Current',
      last_name: 'User',
      stt: { id: 5, name: 'Chicago' },
      regions: [{ id: 3, name: 'Philadelphia' }],
    }
    const store = mockStore({
      auth: {
        user: existingUser,
      },
    })

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
    patch.mockResolvedValue({
      data: apiUserResponse,
      ok: true,
      status: 200,
      error: null,
    })

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions).toEqual([
      { type: PATCH_REQUEST_USER_UPDATE },
      { type: SET_REQUEST_USER_UPDATE },
      {
        type: SET_AUTH,
        payload: {
          user: {
            ...apiUserResponse,
            first_name: 'Current',
            last_name: 'User',
            stt: { id: 5, name: 'Chicago' },
            regions: [{ id: 3, name: 'Philadelphia' }],
          },
        },
      },
    ])
  })

  it('handles missing optional values like regions', async () => {
    const store = mockStore({
      auth: {
        user: {
          id: 'some-id-2',
          first_name: 'Current',
          last_name: 'Smith',
          stt: { id: 1, name: 'Alabama' },
          regions: [],
        },
      },
    })

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
    patch.mockResolvedValue({
      data: apiUserResponse,
      ok: true,
      status: 200,
      error: null,
    })

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions).toEqual([
      { type: PATCH_REQUEST_USER_UPDATE },
      { type: SET_REQUEST_USER_UPDATE },
      { type: SET_AUTH, payload: { user: apiUserResponse } },
    ])
  })

  it('uses API user values when there are no pending requests', async () => {
    const store = mockStore({
      auth: {
        user: {
          first_name: 'Old',
          last_name: 'Name',
          stt: { id: 1, name: 'Alabama' },
          regions: [{ id: 1, name: 'Boston' }],
        },
      },
    })

    const apiUserResponse = {
      id: 'some-id-3',
      first_name: 'John',
      last_name: 'Smith',
      stt: { id: 2, name: 'Alaska' },
      regions: [],
      has_fra_access: false,
      pending_requests: 0,
    }

    patch.mockResolvedValue({
      data: apiUserResponse,
      ok: true,
      status: 200,
      error: null,
    })

    await store.dispatch(
      updateUserRequest({
        firstName: 'John',
        lastName: 'Smith',
        hasFRAAccess: false,
      })
    )

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

    patch.mockResolvedValue({
      data: null,
      ok: false,
      status: 500,
      error: new Error('threw an error'),
    })

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_USER_UPDATE)
    expect(actions[1].type).toBe(SET_REQUEST_USER_UPDATE_ERROR)
  })

  it('clears the state if the API returns no data', async () => {
    const store = mockStore()

    const mockInput = {
      firstName: 'John',
      lastName: 'Smith',
      stt: undefined,
      hasFRAAccess: false,
    }

    patch.mockResolvedValue({
      data: null,
      ok: true,
      status: 200,
      error: null,
    })

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions[0].type).toBe(PATCH_REQUEST_USER_UPDATE)
    expect(actions[1].type).toBe(CLEAR_REQUEST_USER_UPDATE)
  })
})
