import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import { render, screen } from '@testing-library/react'

import Profile from './Profile'
import configureStore from 'redux-mock-store'

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'hi@bye.com',
      first_name: 'john',
      last_name: 'willis',
      roles: [],
      access_request: true,
    },
  },
}

describe('Profile', () => {
  const mockStore = configureStore([thunk])

  it('should display a pending approval message after user access request is made', () => {
    const store = mockStore(initialState)

    render(
      <Provider store={store}>
        <Profile />
      </Provider>
    )
    expect(
      screen.getByText(
        `Your request for access is currently being reviewed by an OFA Admin. We’ll send you an email when it’s been approved.`
      )
    ).toBeInTheDocument()
  })

  it('should not display a pending approval message after user access is approved', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
          access_request: true,
        },
      },
    })

    render(
      <Provider store={store}>
        <Profile />
      </Provider>
    )
    expect(
      screen.queryByText(
        `Your request for access is currently being reviewed by an OFA Admin. We’ll send you an email when it’s been approved.`
      )
    ).not.toBeInTheDocument()
  })

  it("should display user's info during the pending approbal state", () => {
    const store = mockStore(initialState)

    render(
      <Provider store={store}>
        <Profile />
      </Provider>
    )
    expect(screen.getByText('john willis')).toBeInTheDocument()
    expect(screen.getByText('hi@bye.com')).toBeInTheDocument()
  })
})
