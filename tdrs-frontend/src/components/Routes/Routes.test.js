import React from 'react'
import { mount } from 'enzyme'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter } from 'react-router-dom'

import Routes from './Routes'
import SplashPage from '../SplashPage'
import Dashboard from '../Dashboard'

describe('Routes.js', () => {
  const mockStore = configureStore([thunk])

  it('routes "/" to the SplashPage page when user not authenticated', () => {
    const store = mockStore({ auth: { authenticated: false } })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(wrapper.find(SplashPage)).toExist()
  })

  it('routes "/" to the Dashboard page when user is authenticated', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(wrapper.find(Dashboard)).toExist()
  })
})
