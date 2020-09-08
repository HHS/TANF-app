import React from 'react'
import { shallow, mount } from 'enzyme'

import Header from './Header'

describe('Header', () => {
  it('should have a title link', () => {
    const wrapper = shallow(<Header />)
    const title = wrapper.find('a[title="Home"]')
    expect(title).toExist()
    expect(title).toIncludeText('TANF Data Portal')
  })

  it('should have a primary navigation', () => {
    const wrapper = mount(<Header />)
    const welcomeLink = wrapper.find('.usa-nav__link')
    expect(welcomeLink).toExist()
    expect(welcomeLink).toIncludeText('Welcome')
  })

  it('should find menu button', () => {
    const wrapper = mount(<Header />)
    const menuBtn = wrapper.find('.usa-menu-btn')
    expect(menuBtn).toExist()
  })

  it('should call toggleMobileNav when menu button is clicked on mobile', () => {
    const wrapper = mount(<Header />)
    const menuBtn = wrapper.find('button.usa-menu-btn')
    let nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(false)

    menuBtn.simulate('click')

    nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(true)
  })

  it('should close menu overlay when close button is clicked', () => {
    const wrapper = mount(<Header />)
    const menuBtn = wrapper.find('button.usa-menu-btn')
    let nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(false)

    menuBtn.simulate('click')

    nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(true)

    const closeBtn = wrapper.find('button.usa-nav__close')

    closeBtn.simulate('click')

    nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(false)
  })
})
