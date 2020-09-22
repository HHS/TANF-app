import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import Dashboard from './Dashboard'

describe('Dashboard.js', () => {
  const mockStore = configureStore([thunk])

  it('redirects to API logout endpoint when sign-out button is clicked', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })

    const url = 'http://localhost:8080/v1/logout/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = mount(
      <Provider store={store}>
        <Dashboard />
      </Provider>
    )
    wrapper.find('.usa-button').simulate('click', {
      preventDefault: () => {},
    })
    expect(window.location.href).toEqual(url)
  })
})
