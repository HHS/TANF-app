import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import Header from './Header'

describe('Header', () => {
  let initialState = {
    router: { location: { pathname: '/edit-profile' } },
    auth: { user: { email: 'test@test.com' }, authenticated: true },
  }
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

  it("should add usa-current class to Welcome tab when on '/edit-profile'", () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = wrapper.find('.usa-nav__link')

    expect(welcomeTab.hasClass('usa-current')).toEqual(true)
  })

  it("should not add usa-current class to Welcome tab when not on '/edit-profile'", () => {
    initialState = { ...initialState, router: { location: '/' } }
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = wrapper.find('.usa-nav__link')

    expect(welcomeTab.hasClass('usa-current')).toEqual(false)
  })

  it('should log out user when sign out button is clicked', () => {
    const store = mockStore(initialState)
    const url = 'http://localhost:8080/v1/logout/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const signOutLink = wrapper.find('.sign-out-link').first()

    signOutLink.simulate('click')

    expect(window.location.href).toEqual(url)
  })

  it('should have secondaryItems when user is logged in', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const secondaryLinks = wrapper.find('.usa-nav__secondary-item')

    expect(secondaryLinks.length).toEqual(2)
  })

  it('should not have secondaryItems when user is logged out', () => {
    initialState = {
      ...initialState,
      auth: { user: {}, authenticated: false },
    }
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const secondaryLinks = wrapper.find('.usa-nav__secondary-item')

    expect(secondaryLinks.length).toEqual(0)
  })
})
