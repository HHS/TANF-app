import React from 'react'
import thunk from 'redux-thunk'
import { render, screen } from '@testing-library/react'
import configureStore from 'redux-mock-store'
import SiteMap from './SiteMap'
import { Provider } from 'react-redux'

describe('SiteMap', () => {
  const initialState = {
    router: { location: { pathname: '/home' } },
    auth: {
      user: {
        email: 'test@test.com',
        roles: [{ id: 1, name: 'Developer', permissions: [] }],
        access_request: true,
      },
      authenticated: true,
    },
  }

  it('When an authenticated Developer visits the sitemap', () => {
    const mockStore = configureStore([thunk])
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 1, name: 'Developer', permission: [] }],
          access_request: true,
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <SiteMap />
      </Provider>
    )

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  })

  it('When an authenticated Admin visits the sitemap', () => {
    const mockStore = configureStore([thunk])
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 1, name: 'OFA System Admin', permission: [] }],
          access_request: true,
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <SiteMap />
      </Provider>
    )

    const locations = [
      'Home',
      'Privacy Policy',
      'Data Files',
      'Profile',
      'Admin',
    ]
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  })
})
