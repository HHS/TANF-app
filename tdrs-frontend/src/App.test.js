import React from 'react'
import { mount } from 'enzyme'

import GovBanner from './components/GovBanner'
import Header from './components/Header'
import { Alert } from './components/Alert'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import App from './App'

describe('App.js', () => {
  const initialState = {
    alert: {
      show: false,
      type: null,
      heading: null,
      body: null,
    },
    router: {
      location: {
        pathname: '/',
      },
    },
    auth: {
      user: null,
    },
  }
  const mockStore = configureStore([thunk])

  afterEach(() => {
    window.location.href = ''
  })

  it('renders the Gov Banner', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(GovBanner)).toExist()
  })

  it('renders the Header', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(Header)).toExist()
  })

  it('renders the Alert', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(Alert)).toExist()
  })

  it('should redirect to #main-content when space bar is pressed on "skip links" element', () => {
    const url = '#main-content'

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )

    const skipLink = wrapper.find('.usa-skipnav')
    skipLink.simulate('keyPress', {
      charCode: 32,
    })

    expect(window.location.href).toEqual(url)
  })

  it('should do nothing if any key besides space bar is pressed', () => {
    const url = ''

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )

    const skipLink = wrapper.find('.usa-skipnav')
    skipLink.simulate('keyPress', {
      charCode: 25,
    })

    expect(window.location.href).toEqual(url)
  })
})
