import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import {
  updateUserRequest,
  UPDATE_USER_REQUEST_SUCCESS,
} from './mockUpdateUserRequest'

const middlewares = [thunk]
const mockStore = configureStore(middlewares)

describe('updateUserRequest', () => {
  it('dispatches UPDATE_USER_REQUEST_SUCCESS with correct user data', async () => {
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

    const expectedUser = {
      first_name: 'Jane',
      last_name: 'Doe',
      stt: 2,
      regions: [],
      has_fra_access: true,
    }

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions).toEqual([
      {
        type: UPDATE_USER_REQUEST_SUCCESS,
        user: expectedUser,
      },
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

    const expectedUser = {
      first_name: 'John',
      last_name: 'Smith',
      stt: undefined,
      regions: [],
      has_fra_access: false,
    }

    await store.dispatch(updateUserRequest(mockInput))

    const actions = store.getActions()
    expect(actions).toEqual([
      {
        type: UPDATE_USER_REQUEST_SUCCESS,
        user: expectedUser,
      },
    ])
  })
})
