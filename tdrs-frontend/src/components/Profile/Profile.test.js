import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import { render } from '@testing-library/react'

import Profile from './Profile'
import configureStore from 'redux-mock-store'

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'hi@bye.com',
      roles: [],
      access_request: false,
    },
  },
  stts: {
    loading: false,
    sttList: [
      {
        id: 1,
        type: 'state',
        code: 'AL',
        name: 'Alabama',
      },
      {
        id: 2,
        type: 'state',
        code: 'AK',
        name: 'Alaska',
      },
      {
        id: 140,
        type: 'tribe',
        code: 'AK',
        name: 'Aleutian/Pribilof Islands Association, Inc.',
      },
    ],
  },
}

describe('Profile', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch "setAlert" when form is submitted and there is an error', () => {
    const store = mockStore({
      ...initialState,
      requestAccess: {
        ...initialState.requestAccess,
        error: { message: 'This request failed' },
      },
      stts: {
        sttList: [
          {
            id: 1,
            type: 'state',
            code: 'AL',
            name: 'Alabama',
          },
          {
            id: 2,
            type: 'state',
            code: 'AK',
            name: 'Alaska',
          },
          {
            id: 140,
            type: 'tribe',
            code: 'AK',
            name: 'Aleutian/Pribilof Islands Association, Inc.',
          },
        ],
      },
    })
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    render(
      <Provider store={store}>
        <Profile />
      </Provider>
    )
    expect(store.dispatch).toHaveBeenCalled()
  })
})
