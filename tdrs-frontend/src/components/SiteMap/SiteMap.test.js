import React from 'react'
import { render } from '@testing-library/react'

import SiteMap from './SiteMap'

describe('SiteMap', () => {

  describe("When an non-admin user visits the sitemap",() =>{

    const initialState = {
      auth: { authenticated: false, inactive: false },
      roles:[]
    }
    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      it(`renders the $(location) link`, () => {
        const { getByText } = render(<SiteMap />)
        expect(getByText(location)).toBeInTheDocument()
      })
    }

  })
  describe("When an admin user visits the sitemap",() => {

    const initialState = {
      auth: { authenticated: false, inactive: false },
      roles:[{name:"Developer"}]
    }
    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      it(`renders the $(location) link`, () => {
        const { getByText } = render(<SiteMap />)
        expect(getByText(location)).toBeInTheDocument()
      })
    }
  })

  describe("When an unapproved user visits the sitemap",() => {

    const initialState = {
      auth: { authenticated: false, inactive: false },
      roles:[{name:"Developer"}]
    }
    const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile']
    for (let location of locations) {
      it(`renders the $(location) link`, () => {
        const { getByText } = render(<SiteMap />)
        expect(getByText(location)).toBeInTheDocument()
      })
    }
  })

})
