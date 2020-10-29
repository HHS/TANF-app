import React from 'react'
import { shallow } from 'enzyme'

import Unassigned from '.'
import Button from '../Button'

describe('Unassigned', () => {
  it('should have an h1 with "Request Submitted"', () => {
    const wrapper = shallow(<Unassigned />)

    const h1 = wrapper.find('h1')

    expect(h1).toExist()
    expect(h1.text()).toEqual('Request Submitted')
  })

  it('should have a subheading with "An administrator will be in touch soon to confirm your access!"', () => {
    const wrapper = shallow(<Unassigned />)

    const p = wrapper.find('p')

    expect(p).toExist()
    expect(p.text()).toEqual(
      'An administrator will be in touch soon to confirm your access!'
    )
  })

  it('should have a sign out button', () => {
    const wrapper = shallow(<Unassigned />)

    const button = wrapper.find(Button)

    expect(button).toExist()
  })
})
