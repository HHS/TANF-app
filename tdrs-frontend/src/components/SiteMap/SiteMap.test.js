import React from 'react'
import thunk from 'redux-thunk'
import { render } from '@testing-library/react'
import configureStore from 'redux-mock-store'
import SiteMap from './SiteMap'
import { Provider } from 'react-redux'
import { mount } from 'enzyme'

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
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'Developer', permissions: [] }],
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile', 'Admin']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  })

  it('When an authenticated OFA System Admin visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'OFA System Admin', permissions: [] }],
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile', 'Admin']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  }) 

  it('When an authenticated ACF OCIO visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'ACF OCIO', permissions: [] }],
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile', 'Admin']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
  })
  it('When an authenticated Data Analyst visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'Data Analyst', permissions: [] }],
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
    const wrapper = mount(<SiteMap user={user}></SiteMap>)
    expect(wrapper.html()).not.toContain('Admin')
    expect(wrapper.html()).toContain('Home')
  }) 
})
