import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import Header from './Header'

describe('Header', () => {
  let initialState = { router: { location: { pathname: '/' } } }
  const mockStore = configureStore([thunk])

  it('should have a title link', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const title = wrapper.find('a[title="Home"]')
    expect(title).toExist()
    expect(title).toIncludeText('TANF Data Portal')
  })

  it('should have a primary navigation', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const welcomeLink = wrapper.find('.usa-nav__link')
    expect(welcomeLink).toExist()
    expect(welcomeLink).toIncludeText('Welcome')
  })

  it('should find menu button', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const menuBtn = wrapper.find('.usa-menu-btn')
    expect(menuBtn).toExist()
  })

  it('should call toggleMobileNav when menu button is clicked on mobile', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const menuBtn = wrapper.find('button.usa-menu-btn')
    let nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(false)

    menuBtn.simulate('click')

    nav = wrapper.find('.usa-nav')

    expect(nav.hasClass('is-visible')).toEqual(true)
  })

  it('should close menu overlay when close button is clicked', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
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

  it("should add usa-current class to Welcome tab when on '/'", () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = wrapper.find('.usa-nav__link')

    expect(welcomeTab.hasClass('usa-current')).toEqual(true)
  })

  it("should not add usa-current class to Welcome tab when not on '/'", () => {
    initialState = { router: { location: '/dashboard' } }
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = wrapper.find('.usa-nav__link')

    expect(welcomeTab.hasClass('usa-current')).toEqual(false)
  })
})
