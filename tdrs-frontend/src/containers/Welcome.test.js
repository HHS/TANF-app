import React from 'react'
import { shallow } from 'enzyme'

import Welcome from './Welcome'

describe('Welcome.js', () => {
  it('renders a welcome message', () => {
    const wrapper = shallow(<Welcome />)
    expect(wrapper.find('h1')).toIncludeText('Welcome to TDRS!')
  })
})
