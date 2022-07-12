import React from 'react'
import { render } from '@testing-library/react'

import SiteMap from './SiteMap'

describe('SiteMap', () => {

  const initialState = {
    auth: { authenticated: false, inactive: false },
  }
  const locations = ['Home', 'Privacy Policy', 'Data Files', 'Profile', 'Admin']
  for (let location of locations) {
    it(`renders the $(location) link`, () => {
      const { getByText } = render(<SiteMap />)
      expect(getByText(location)).toBeInTheDocument()
    })
  }
})
