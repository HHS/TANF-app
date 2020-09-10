import React from 'react'
import { mount } from 'enzyme'

import SignUp from './SignUp'

describe('SignUp', () => {
  it('should have a card with header Request Access', () => {
    const wrapper = mount(<SignUp />)
    const cardHeader = wrapper.find('.usa-card__heading')

    expect(cardHeader).toExist()
  })

  it('should have a first name input', () => {
    const wrapper = mount(<SignUp />)

    const nameInput = wrapper.find('#first-name')

    expect(nameInput).toExist()
  })

  it('should have a last name input', () => {
    const wrapper = mount(<SignUp />)

    const nameInput = wrapper.find('#last-name')

    expect(nameInput).toExist()
  })

  it('should have a submit button', () => {
    const wrapper = mount(<SignUp />)

    const nameInput = wrapper.find('button[type="submit"]')

    expect(nameInput).toExist()
  })
})
