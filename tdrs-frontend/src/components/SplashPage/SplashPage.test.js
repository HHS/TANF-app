import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Redirect } from 'react-router-dom'

import SplashPage from './SplashPage'

describe('SplashPage', () => {
  const initialState = { auth: { authenticated: false } }
  const mockStore = configureStore([thunk])

  it('renders a sign in header', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    const hero = wrapper.find('.usa-hero__callout')
    expect(hero.find('h1')).toIncludeText('Sign into TANF Data Portal')
  })

  it('does not render the page while auth is loading', () => {
    const store = mockStore({ auth: { loading: true } })
    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    expect(wrapper.find('h1')).not.toIncludeText('SplashPage to TDRS!')
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
        <SplashPage />
      </Provider>
    )
    wrapper.find('button').simulate('click', {
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
          <SplashPage />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper).toContainReact(<Redirect to="/dashboard" />)
  })
})
