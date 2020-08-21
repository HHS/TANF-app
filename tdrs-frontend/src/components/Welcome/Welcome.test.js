import React from 'react'
import { shallow } from 'enzyme'

import { Button } from '@trussworks/react-uswds'
import Welcome from './Welcome'

describe('Welcome.js', () => {
  it('renders a welcome message', () => {
    const wrapper = shallow(<Welcome />)
    expect(wrapper.find('h1')).toIncludeText('Welcome to TDRS!')
  })

  // it('initiates authorization when sign-in button is clicked', () => {
  //   const wrapper = shallow(<Welcome />)

  //   wrapper.find(Button).simulate('click', {
  //     preventDefault: () => {},
  //   })

  //   expect(false).toExist()
  //   expect(window.location).toHaveBeenCalled()
  // })
})
