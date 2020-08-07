import React from 'react'
import { shallow } from 'enzyme'

import { GovBanner } from '@trussworks/react-uswds'
import App from './App'

describe('App.js', () => {
  it('renders the Gov Banner', () => {
    const wrapper = shallow(<App />)
    expect(wrapper.find(GovBanner)).toExist()
  })
})
