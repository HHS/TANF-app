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

  it('should have a navigation link for Welcome', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const welcomeLink = wrapper.find('#welcome')
    expect(welcomeLink).toExist()
    expect(welcomeLink).toIncludeText('Welcome')
  })

  it('should have a navigation link for Reports', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const reportsLink = wrapper.find('#reports')
    expect(reportsLink).toExist()
    expect(reportsLink).toIncludeText('Reports')
  })

  it('should have a navigation link for Profile', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const profileLink = wrapper.find('#profile')
    expect(profileLink).toExist()
    expect(profileLink).toIncludeText('Profile')
  })

  it('should have a navigation link for Admin', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )
    const adminLink = wrapper.find('#admin')
    expect(adminLink).toExist()
    expect(adminLink).toIncludeText('Admin')
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

  it("should add usa-current class to Welcome tab when on '/welcome'", () => {
    const store = mockStore({
      ...initialState,
      router: { location: { pathname: '/welcome' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = wrapper.find('#welcome')

    expect(welcomeTab.hasClass('usa-current')).toEqual(true)
  })

  it("should add usa-current class to Reports tab when on '/reports'", () => {
    const store = mockStore({
      ...initialState,
      router: { location: { pathname: '/reports' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const reportsTab = wrapper.find('#reports')

    expect(reportsTab.hasClass('usa-current')).toEqual(true)
  })

  it("should add usa-current class to Reports tab when on '/reports/*'", () => {
    const store = mockStore({
      ...initialState,
      router: { location: { pathname: '/reports/upload' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const reportsTab = wrapper.find('#reports')

    expect(reportsTab.hasClass('usa-current')).toEqual(true)
  })

  it("should add usa-current class to Profile tab when on '/reports'", () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const profileTab = wrapper.find('#profile')

    expect(profileTab.hasClass('usa-current')).toEqual(true)
  })

  it("should add usa-current class to Admin tab when on '/reports'", () => {
    const store = mockStore({
      ...initialState,
      router: { location: { pathname: '/admin' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const adminTab = wrapper.find('#admin')

    expect(adminTab.hasClass('usa-current')).toEqual(true)
  })

  it("should not add usa-current class to Welcome tab when not on '/edit-profile'", () => {
    initialState = { ...initialState, router: { location: { pathname: '/' } } }
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Header />
      </Provider>
    )

    const welcomeTab = wrapper.find('#welcome')

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
    expect(secondaryLinks.first().text()).toEqual('test@test.com')
    expect(secondaryLinks.last().text()).toEqual('Sign Out')
  })

  it('should have one visible secondaryItem when user is logged out', () => {
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

    expect(secondaryLinks.first().hasClass('display-none')).toBeTruthy()
    expect(secondaryLinks.last().text()).toEqual('Sign In')
  })
})
