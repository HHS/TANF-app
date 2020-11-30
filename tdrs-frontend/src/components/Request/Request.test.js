import React from 'react'
import { shallow } from 'enzyme'

import Request from '.'
import Button from '../Button'

describe('Request', () => {

  it('should have a subheading with "An administrator will be in touch soon to confirm your access!"', () => {
    const wrapper = shallow(<Request />)

    const p = wrapper.find('p')

    expect(p).toExist()
    expect(p.text()).toEqual(
      'An administrator will be in touch soon to confirm your access!'
    )
  })

  it('should have a sign out button', () => {
    const wrapper = shallow(<Request />)

    const button = wrapper.find(Button)

    expect(button).toExist()
  })

  it('should sign out when the sign out button is clicked', () => {
    const url = 'http://localhost:8080/v1/logout/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })
    const wrapper = shallow(<Request />)

    const button = wrapper.find(Button)

    button.simulate('click', {
      preventDefault: () => {},
    })

    expect(window.location.href).toEqual(url)
  })
})
