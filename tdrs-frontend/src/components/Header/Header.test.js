import React from 'react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter } from 'react-router'

import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import Header from './Header'
import { permissions } from './developer_permissions'

describe('Header', () => {
  const initialState = {
    router: { location: { pathname: '/profile' } },
    auth: {
      user: {
        email: 'test@test.com',
        roles: [{ id: 1, name: 'Developer', permissions }],
        access_request: true,
        account_approval_status: 'Approved',
      },
      authenticated: true,
    },
  }

  const mockStore = configureStore([thunk])

  it('should have a title link', () => {
    const store = mockStore(initialState)
    render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    const title = screen.getByText('TANF Data Portal')
    expect(title).toBeInTheDocument()
  })

  it('should have a navigation link for Welcome', () => {
    const store = mockStore(initialState)
    render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )
    const welcomeLink = screen.getByText('Home')
    expect(welcomeLink).toBeInTheDocument()
    const dataFilesLink = screen.getByText('TANF Data Files')
    expect(dataFilesLink).toBeInTheDocument()
    const profileLink = screen.getByText('Profile')
    expect(profileLink).toBeInTheDocument()
    const adminLink = screen.getByText('Admin')
    expect(adminLink).toBeInTheDocument()
  })

  it('should NOT have a navigation link for Admin when user is NOT a OFA System Admin', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'test@test.com',
          roles: [{ id: 2, name: 'Data Prepper', permissions: [] }],
        },
      },
    })

    render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )
    const adminLink = screen.queryByText('Admin')
    expect(adminLink).not.toBeInTheDocument()
  })

  it("should add usa-current class to Welcome tab when on '/home'", () => {
    const store = mockStore({
      ...initialState,
      router: { location: { pathname: '/home' } },
    })

    render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    const welcomeTab = screen.getByText('Home')
    expect(welcomeTab.parentNode).toHaveClass('usa-current')
  })

  it("should add usa-current class to Data Files tab when on '/data-files'", () => {
    const store = mockStore({
      ...initialState,
      router: { location: { pathname: '/data-files' } },
    })

    render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    const dataFilesTab = screen.getByText('TANF Data Files')

    expect(dataFilesTab.parentNode).toHaveClass('usa-current')
  })

  it("should add usa-current class to Profile tab when on '/profile'", () => {
    const store = mockStore(initialState)
    const { container } = render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    const profileTab = container.querySelector('#profile')

    expect(profileTab).toHaveClass('usa-current')
  })

  it("should not add usa-current class to Welcome tab when not on '/'", () => {
    const state = { ...initialState, router: { location: { pathname: '/' } } }
    const store = mockStore(state)
    render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    const welcomeTab = screen.getByText('Home')
    expect(welcomeTab).not.toHaveClass('usa-current')
  })

  it('should have secondaryItems when user is logged in', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    const secondaryLinks = container.querySelectorAll(
      '.usa-nav__secondary-item'
    )

    expect(secondaryLinks.length).toEqual(2)
    expect(secondaryLinks[0].textContent).toEqual('test@test.com')
  })

  it('should NOT show any nav items when the user is NOT logged in', () => {
    const state = {
      ...initialState,
      auth: { user: {}, authenticated: false },
    }

    const store = mockStore(state)

    const { queryByText } = render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    expect(queryByText('Welcome')).not.toBeInTheDocument()
    expect(queryByText('TANF Data Files')).not.toBeInTheDocument()
    expect(queryByText('Profile')).not.toBeInTheDocument()
    expect(queryByText('Admin')).not.toBeInTheDocument()
  })

  it('should NOT show data-files nav item when the user does not have view_datafile and add_datafile permissions', () => {
    const state = {
      ...initialState,
      auth: {
        user: {
          email: 'test@test.com',
          roles: [{ id: 1, name: 'Developer', permissions: [] }],
          access_request: true,
          account_approval_status: 'Approved',
        },
        authenticated: true,
      },
    }

    const store = mockStore(state)

    const { queryByText } = render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    expect(queryByText('TANF Data Files')).not.toBeInTheDocument()
    expect(queryByText('Profile')).toBeInTheDocument()
    expect(queryByText('Admin')).toBeInTheDocument()
  })

  it('should NOT show data-files nav item when the user is not in an approved status', () => {
    const state = {
      ...initialState,
      auth: {
        user: {
          email: 'test@test.com',
          roles: [
            {
              id: 1,
              name: 'Developer',
              permissions: ['add_datafile', 'view_datafile'],
            },
          ],
          account_approval_status: 'Pending',
        },
        authenticated: true,
      },
    }

    const store = mockStore(state)

    const { queryByText } = render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    expect(queryByText('TANF Data Files')).not.toBeInTheDocument()
    expect(queryByText('Profile')).toBeInTheDocument()
    expect(queryByText('Admin')).not.toBeInTheDocument()
  })

  it('should show data-files nav item when the user has view_datafile and add_datafile permissions and is approved', () => {
    const store = mockStore(initialState)

    const { queryByText } = render(
      <MemoryRouter>
        <Provider store={store}>
          <Header />
        </Provider>
      </MemoryRouter>
    )

    expect(queryByText('TANF Data Files')).toBeInTheDocument()
    expect(queryByText('Profile')).toBeInTheDocument()
    expect(queryByText('Admin')).toBeInTheDocument()
  })
})
