import React from 'react'
import { shallow } from 'enzyme'

import Footer from './Footer'

describe('Footer', () => {
  it('renders a sign in header', () => {
    const wrapper = shallow(<Footer />)
    expect(wrapper.find('img')).toExist()
  })
})
