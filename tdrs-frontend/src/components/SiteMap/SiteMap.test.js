import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import { mount } from 'enzyme'
import { render, screen } from '@testing-library/react'
import configureStore from 'redux-mock-store'
import SplashPage from '../SplashPage'
import SiteMap from './SiteMap'
import { permissions } from '../Header/developer_permissions'
import PrivateRoute from '../PrivateRoute'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

describe('SiteMap', () => {
  it('When a non authenticated user visits the splash page do not show sitemap', () => {
    const initialState = {
      auth: { authenticated: false, inactive: false },
      roles: [],
    }
    const mockStore = configureStore([thunk])

    const store = mockStore(initialState)

    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )

    const footer = wrapper.find('footer')
    expect(footer).not.toIncludeText('Site Map')
  })

  it('When an authenticated developer visits the splash page show sitemap', () => {
    const initialState = {
      router: { location: { pathname: '/home' } },
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
    const store = mockStore(initialState)

    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )

    const footer = wrapper.find('footer')
    expect(footer.find('.usa-footer')).toIncludeText('Site Map')
  })

  it('When an authenticated admin visits the splash page show sitemap', () => {
    const initialState = {
      router: { location: { pathname: '/home' } },
      auth: {
        user: {
          email: 'test@test.com',
          roles: [{ id: 1, name: 'Admin', permissions }],
          access_request: true,
        },
        authenticated: true,
      },
    }

    const mockStore = configureStore([thunk])
    const store = mockStore(initialState)

    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/home', '/']}>
          <Routes>
            <Route
              exact
              path="/home"
              element={
                <PrivateRoute title="Welcome to TDP">
                  <SplashPage />
                </PrivateRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </Provider>
    )

    const footer = wrapper.find('footer')
    expect(footer.find('.usa-footer')).not.toIncludeText('Site Map')
  })

  it('When an non-authenticated user visits the sitemap', () => {
    const initialState = {
      auth: { authenticated: false, inactive: false },
      roles: [],
    }
    const mockStore = configureStore([thunk])
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    const footer = wrapper.find('footer')
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  })

  it('When an authenticated user visits the sitemap', () => {
    const initialState = {
      auth: { authenticated: false, inactive: false },
      roles: [],
    }
    const mockStore = configureStore([thunk])
    const store = mockStore(initialState)
    const { getByText } = render(<SiteMap store={store} />)

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  })
})
