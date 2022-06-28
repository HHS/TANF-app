import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import { fireEvent, render, screen } from '@testing-library/react'

import Profile from './Profile'
import configureStore from 'redux-mock-store'

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'test@example.com',
      first_name: 'Bob',
      last_name: 'Belcher',
      roles: [],
      access_request: true,
      stt: {
        name: 'No one really knows',
        id: 999,
        type: 'fictional district',
        code: '??',
        region: 9999,
      },
    },
  },
}
describe('Profile', () => {
  const mockStore = configureStore([thunk])

  let location
  const mockLocation = new URL('https://example.com')

  beforeEach(() => {
    location = window.location
    mockLocation.replace = jest.fn()
    // You might need to mock other functions as well
    // location.assign = jest.fn();
    // location.reload = jest.fn();
    delete window.location
    window.location = mockLocation
  })

  afterEach(() => {
    window.location = location
  })

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
  it('should display all information about the user correctly when approved', () => {
    const store = mockStore(initialState)

    render(
      <Provider store={store}>
        <Profile />
      </Provider>
    )
    expect(screen.getByText('Bob Belcher')).toBeInTheDocument()
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByText('No one really knows')).toBeInTheDocument()
    expect(screen.getByText('Region 9999')).toBeInTheDocument()
  })

  it('should navigate to external login client settings', () => {
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

    fireEvent.click(screen.getByText('Manage Your Account at'))
    expect(window.location.href).toBe(
      'https://idp.int.identitysandbox.gov/account'
    )
  })

  it("should display user's info during the pending approval state", () => {
    const store = mockStore(initialState)

    render(
      <Provider store={store}>
        <Profile />
      </Provider>
    )
    expect(screen.getByText('Bob Belcher')).toBeInTheDocument()
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
    expect(screen.getByText('No one really knows')).toBeInTheDocument()
    expect(screen.getByText('Region 9999')).toBeInTheDocument()
  })
})
