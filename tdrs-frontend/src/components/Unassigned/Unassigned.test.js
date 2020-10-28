import React from 'react'
import { shallow } from 'enzyme'

import Unassigned from '.'

describe('Unassigned', () => {
  it('should have a card group', () => {
    const wrapper = shallow(<Unassigned />)

    const cardGroup = wrapper.find('.usa-card-group')

    expect(cardGroup).toExist()
  })

  it('should have a card', () => {
    const wrapper = shallow(<Unassigned />)

    const card = wrapper.find('.usa-card')

    expect(card).toExist()
  })
  it('should have a card header', () => {
    const wrapper = shallow(<Unassigned />)

    const cardHeader = wrapper.find('.usa-card__header')

    expect(cardHeader).toExist()
    expect(cardHeader.text()).toEqual('Request Submitted')
  })
  it('should have a card body', () => {
    const wrapper = shallow(<Unassigned />)

    const cardBody = wrapper.find('.usa-card__body')

    expect(cardBody).toExist()
    expect(cardBody.text()).toEqual(
      'An administrator will be in touch soon to confirm your access!'
    )
  })
})
