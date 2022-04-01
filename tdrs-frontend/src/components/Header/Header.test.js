import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

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
      },
      authenticated: true,
    },
  }

  const mockStore = configureStore([thunk])

  it('should have a title link', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const title = screen.getByLabelText('Home')
    expect(title).toBeInTheDocument()
    expect(title).toHaveTextContent('TANF Data Portal')
  })

  it('should have a navigation link for Welcome', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const welcomeLink = screen.getByText('Home')
    expect(welcomeLink).toBeInTheDocument()
    const dataFilesLink = screen.getByText('Data Files')
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
      <Provider store={store}>
        <Header />
      </Provider>
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
      <Provider store={store}>
        <Header />
      </Provider>
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
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const dataFilesTab = screen.getByText('Data Files')

    expect(dataFilesTab.parentNode).toHaveClass('usa-current')
  })

  it("should add usa-current class to Profile tab when on '/profile'", () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const profileTab = wrapper.find('#profile')

    expect(profileTab.hasClass('usa-current')).toEqual(true)
  })

  it("should not add usa-current class to Welcome tab when not on '/'", () => {
    const state = { ...initialState, router: { location: { pathname: '/' } } }
    const store = mockStore(state)
    render(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = screen.getByText('Home')
    expect(welcomeTab).not.toHaveClass('usa-current')
  })

  it('should have secondaryItems when user is logged in', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const secondaryLinks = wrapper.find('.usa-nav__secondary-item')

    expect(secondaryLinks.length).toEqual(2)
    expect(secondaryLinks.first().text()).toEqual('test@test.com')
  })

  it('should NOT show any nav items when the user is NOT logged in', () => {
    const state = {
      ...initialState,
      auth: { user: {}, authenticated: false },
    }

    const store = mockStore(state)

    const { queryByText } = render(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    expect(queryByText('Welcome')).not.toBeInTheDocument()
    expect(queryByText('Data Files')).not.toBeInTheDocument()
    expect(queryByText('Profile')).not.toBeInTheDocument()
    expect(queryByText('Admin')).not.toBeInTheDocument()
  })
})
