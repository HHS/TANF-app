import React from 'react'
import { render } from '@testing-library/react'
import SiteMap from './SiteMap'
import { mount } from 'enzyme'

describe('SiteMap', () => {
  it('When an authenticated Developer visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [{ id: 1, name: 'Developer', permissions: [] }],
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

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
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

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
      access_request: true,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

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

  it('When an authenticated user that does not yet have access visits the sitemap', () => {
    const user = {
      email: 'hi@bye.com',
      roles: [],
      access_request: false,
    }

    const { getByText } = render(<SiteMap user={user}></SiteMap>)

    const locations = [
      'Home',
      'Privacy Policy',
      'Vulnerability Disclosure Policy',
      'Profile',
    ]
    for (let location of locations) {
      expect(getByText(location)).toBeInTheDocument()
    }
    const wrapper = mount(<SiteMap user={user}></SiteMap>)
    expect(wrapper.html()).not.toContain('Admin')
    expect(wrapper.html()).toContain('Home')
  })
})
