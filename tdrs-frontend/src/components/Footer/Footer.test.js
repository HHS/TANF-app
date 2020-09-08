import React from 'react'
import { shallow } from 'enzyme'

import Footer from './Footer'

describe('Footer', () => {
  it('renders the children & families logo', () => {
    const wrapper = shallow(<Footer />)
    expect(wrapper.find('img')).toExist()
  })
})
