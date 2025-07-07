import React from 'react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import { mount } from 'enzyme'
import { fireEvent, render } from '@testing-library/react'
import configureStore from 'redux-mock-store'
import IdleTimer from './IdleTimer'
import { FETCH_AUTH } from '../../actions/auth'

describe('IdleTimer', () => {
  const mockStore = configureStore([thunk])

  it('should have a modal with an id of "timeoutModal"', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = wrapper.find('#timeoutModal')

    expect(modal).toExist()
  })

  it('should start with a className of display-none', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = wrapper.find('#timeoutModal')

    expect(modal.hasClass('display-none')).toBeTruthy()
  })

  it('should change to a className of display-block after 2 seconds', () => {
    const url = 'http://localhost:8080/v1/logout/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })
    jest.useFakeTimers()
    let start = Date.now()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const { container } = render(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = container.querySelector('#timeoutModal')
    expect(modal.classList.contains('display-block')).not.toBeTruthy()

    React.act(() => {
      jest.setSystemTime(start + 1200000)
      fireEvent.focus(document)
    })

    expect(modal.classList.contains('display-block')).toBeTruthy()
  })

  it('should change window location to sign out url when sign out button is clicked on session timeout modal', () => {
    const url = 'http://localhost:8080/v1/logout/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const signOutButton = wrapper.find('.sign-out').hostNodes()

    expect(signOutButton).toExist()

    signOutButton.simulate('click')

    expect(window.location.href).toEqual(url)
  })

  it('should call dispatch method when `Stay Signed In` button is clicked', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const wrapper = mount(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const staySignedInButton = wrapper.find('.renew-session').hostNodes()

    staySignedInButton.simulate('click')

    expect(store.dispatch).toHaveBeenCalledTimes(1)
    expect(store.getActions()[0].type).toEqual(FETCH_AUTH)
  })

  it('should focus `Stay Signed In` button if tab is pressed when modal is open', () => {
    jest.useFakeTimers()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    let start = Date.now()
    const { container } = render(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = container.querySelector('#timeoutModal')
    const staySignedInButton = container.querySelector('.renew-session')

    React.act(() => {
      jest.setSystemTime(start + 1200000)
      fireEvent.focus(document)
    })

    fireEvent.keyDown(modal, { keyCode: 9 })

    expect(document.activeElement).toEqual(staySignedInButton)
  })

  it('should focus `Sign Out Now` button if tab and shift are pressed when modal is open', () => {
    jest.useFakeTimers()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    let start = Date.now()
    const { container } = render(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = container.querySelector('#timeoutModal')
    const signOutButton = container.querySelector('.sign-out')

    React.act(() => {
      jest.setSystemTime(start + 1200000)
      fireEvent.focus(document)
    })

    fireEvent.keyDown(modal, { shiftKey: true, keyCode: 9 })

    expect(document.activeElement).toEqual(signOutButton)
  })

  it('should dispatch fetchAuth 3 seconds after an action', () => {
    jest.useFakeTimers()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })

    const { container } = render(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    fireEvent.mouseMove(container)

    React.act(() => {
      jest.runAllTimers()
    })

    const actions = store.getActions()

    expect(actions[0].type).toBe(FETCH_AUTH)
  })

  it('should not dispatch fetchAuth if the modal is open', () => {
    jest.useFakeTimers()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const wrapper = mount(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    wrapper.simulate('mousemove')

    expect(store.dispatch).toHaveBeenCalledTimes(0)
  })

  it('should handle tab key when document.activeElement is the first element', () => {
    jest.useFakeTimers()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    let start = Date.now()
    const { container } = render(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = container.querySelector('#timeoutModal')
    const staySignedInButton = container.querySelector('.renew-session')

    // Make the modal visible
    React.act(() => {
      jest.setSystemTime(start + 1200000)
      fireEvent.focus(document)
    })

    // Set focus to the first button
    staySignedInButton.focus()
    expect(document.activeElement).toEqual(staySignedInButton)

    // Press tab without shift
    fireEvent.keyDown(modal, { keyCode: 9 })

    // First button should still have focus (branch on line 66)
    expect(document.activeElement).toEqual(staySignedInButton)
  })

  it('should handle shift+tab key when document.activeElement is the last element', () => {
    jest.useFakeTimers()
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    let start = Date.now()
    const { container } = render(
      <Provider store={store}>
        <IdleTimer />
      </Provider>
    )

    const modal = container.querySelector('#timeoutModal')
    const signOutButton = container.querySelector('.sign-out')

    // Make the modal visible
    React.act(() => {
      jest.setSystemTime(start + 1200000)
      fireEvent.focus(document)
    })

    // Set focus to the last button
    signOutButton.focus()
    expect(document.activeElement).toEqual(signOutButton)

    // Press shift+tab
    fireEvent.keyDown(modal, { shiftKey: true, keyCode: 9 })

    // Last button should still have focus (branch on line 77)
    expect(document.activeElement).toEqual(signOutButton)
  })
})
