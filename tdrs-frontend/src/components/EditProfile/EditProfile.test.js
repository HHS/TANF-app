import React from 'react'
import { mount } from 'enzyme'
import {Helmet} from 'react-helmet'

import EditProfile from './EditProfile'

describe('EditProfile', () => {
  it('should have a card with header Request Access', () => {
    const wrapper = mount(<EditProfile />)
    const h1 = wrapper.find('h1')

    expect(h1).toExist()
    expect(h1.text()).toEqual('Request Access')
  })

  it('should have a page title with Request Access in it',() => {
    const wrapper = mount( <EditProfile />)

    expect(Helmet.peek().title.join("")).toEqual('Request Access - TDP - TANF Data Portal')
  })

  it('should have a first name input', () => {
    const wrapper = mount(<EditProfile />)

    const nameInput = wrapper.find('#first-name')

    expect(nameInput).toExist()
  })

  it('should have a last name input', () => {
    const wrapper = mount(<EditProfile />)

    const nameInput = wrapper.find('#last-name')

    expect(nameInput).toExist()
  })

  it('should have a submit button', () => {
    const wrapper = mount(<EditProfile />)

    const submitBtn = wrapper.find('button[type="submit"]')

    expect(submitBtn).toExist()
  })
})
