import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Redirect } from 'react-router-dom'
import { Button } from '@trussworks/react-uswds'

import Welcome from './Welcome'

describe('Welcome.js', () => {
  const initialState = { auth: { authenticated: false } }
  const mockStore = configureStore([thunk])

  it('renders a welcome message', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )
    expect(wrapper.find('h1')).toIncludeText('Welcome to TDRS!')
  })

  it('redirects to API login endpoint when sign-in button is clicked', () => {
    const store = mockStore(initialState)

    const url = 'http://localhost:8080/v1/login/oidc'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const wrapper = mount(
      <Provider store={store}>
        <Welcome />
      </Provider>
    )
    wrapper.find(Button).simulate('click', {
      preventDefault: () => {},
    })
    expect(window.location.href).toEqual(url)
  })

  it('redirects to /dashboard when user is already authenticated', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Welcome />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper).toContainReact(<Redirect to="/dashboard" />)
  })
})
