import React from 'react'
import { render } from '@testing-library/react'
import SiteMap from './SiteMap'
import { mount } from 'enzyme'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

describe('SiteMap', () => {
  const mockStore = configureStore([thunk])

  it('When an authenticated Developer visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'Developer', permissions: [] }],
      account_approval_status: 'Approved',
    }

    const initialState = {
      auth: { user },
    }

    const store = mockStore(initialState)

    const { getByText } = render(
      <Provider store={store}>
        <SiteMap user={user}></SiteMap>
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

  it('When an authenticated OFA System Admin visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
      account_approval_status: 'Approved',
    }

    const initialState = {
      auth: { user },
    }

    const store = mockStore(initialState)

    const { getByText } = render(
      <Provider store={store}>
        <SiteMap user={user}></SiteMap>
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

  it('When an authenticated ACF OCIO visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'ACF OCIO', permissions: [] }],
      account_approval_status: 'Approved',
    }

    const initialState = {
      auth: { user },
    }

    const store = mockStore(initialState)

    const { getByText } = render(
      <Provider store={store}>
        <SiteMap user={user}></SiteMap>
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

  it('When an authenticated Data Analyst visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'Data Analyst', permissions: [] }],
      account_approval_status: 'Approved',
    }

    const initialState = {
      auth: { user },
    }

    const store = mockStore(initialState)

    const { getByText, queryByText } = render(
      <Provider store={store}>
        <SiteMap user={user}></SiteMap>
      </Provider>
    )

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }

    expect(queryByText('Admin')).not.toBeInTheDocument()
  })

  it('When an authenticated user that does not yet have access visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [],
      account_approval_status: 'Pending',
    }

    const initialState = {
      auth: { user },
    }

    const store = mockStore(initialState)

    const { getByText, queryByText } = render(
      <Provider store={store}>
        <SiteMap user={user}></SiteMap>
      </Provider>
    )

    const locations = [
      'Home',
      'Privacy Policy',
      'Vulnerability Disclosure Policy',
      'Profile',
    ]
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }

    expect(queryByText('Admin')).not.toBeInTheDocument()
  })
})
