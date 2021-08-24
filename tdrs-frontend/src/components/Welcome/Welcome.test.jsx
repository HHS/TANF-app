import React from 'react'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import Welcome from './Welcome'

describe('Welcome', () => {
  const initialState = {
    auth: {
      authenticated: true,
      user: {
        email: 'hi@bye.com',
        roles: [],
      },
    },
  }
  const mockStore = configureStore([thunk])

  it('should render the welcome page with the request access subheader', () => {
    const store = mockStore(initialState)
    const { getByText } = render(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )

    const header = getByText(
      `Your request for access is currently being reviewed by an OFA Admin. We'll send you an email when it's been approved.`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the welcome page with the user's current role", () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 1, name: 'OFA Admin', permission: [] }],
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )

    const header = getByText(
      `You've been approved as a(n) OFA Admin. You'll be able to do the following in TDP:`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the welcome page with the user's OFA admin role", () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 2, name: 'Data Analyst', permission: [] }],
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )

    const header = getByText(
      `You've been approved as a(n) Data Analyst. You'll be able to do the following in TDP:`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the welcome page with the user's Data Analyst role and permissions", () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [
            {
              id: 1,
              name: 'Data Analyst',
              permissions: [
                {
                  id: 8,
                  codename: 'view_logentry',
                  name: 'Can view log entry',
                },
                {
                  id: 49,
                  codename: 'add_datafile',
                  name: 'Can add data file',
                },
                {
                  id: 52,
                  codename: 'view_datafile',
                  name: 'Can view data file',
                },
                {
                  id: 37,
                  codename: 'add_user',
                  name: 'Can add user',
                },
                {
                  id: 38,
                  codename: 'change_user',
                  name: 'Can change user',
                },
                {
                  id: 40,
                  codename: 'view_user',
                  name: 'Can view user',
                },
              ],
            },
          ],
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )

    expect(
      getByText(
        `You've been approved as a(n) Data Analyst. You'll be able to do the following in TDP:`
      )
    ).toBeInTheDocument()
    expect(getByText('Can view log entry')).toBeInTheDocument()
    expect(getByText('Can change user')).toBeInTheDocument()
    expect(getByText('Can add user')).toBeInTheDocument()
    expect(getByText('Can view log entry')).toBeInTheDocument()
    expect(getByText('Can add data file')).toBeInTheDocument()
  })

  it('should redirect the page when a user clicks the logout button', async () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )

    fireEvent.click(screen.getByText('Sign Out'))
  })
})
