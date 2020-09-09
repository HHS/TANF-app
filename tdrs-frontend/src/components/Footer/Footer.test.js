import React from 'react'
import { mount } from 'enzyme'

import Footer from './Footer'

describe('Footer', () => {
  it('renders the children & families logo', () => {
    const wrapper = mount(<Footer />)
    expect(wrapper.find('img')).toExist()
  })
})
