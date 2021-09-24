import React from 'react'
import { mount } from 'enzyme'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter } from 'react-router-dom'
import NoMatch from '../NoMatch'

import Routes from './Routes'
import SplashPage from '../SplashPage'
import Welcome from '../Welcome'

describe('Routes.js', () => {
  const mockStore = configureStore([thunk])

  it('routes to a 404 page when there is no matching route', () => {
    const store = mockStore({
      auth: { authenticated: false },
      stts: { sttList: [], loading: false },
      requestAccess: {
        requestAccess: false,
        loading: false,
        user: {},
      },
      reports: {
        year: 2020,
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/IdontExist']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(NoMatch))
  })

  it('routes "/" to the SplashPage page when user not authenticated', () => {
    const store = mockStore({
      auth: { authenticated: false },
      stts: { sttList: [], loading: false },
      requestAccess: {
        requestAccess: false,
        loading: false,
        user: {},
      },
      reports: {
        year: 2020,
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(wrapper.find(SplashPage)).toExist()
  })

  it('routes "/" to the Edit-Profile page when user is authenticated', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
      stts: { sttList: [], loading: false },
      requestAccess: {
        requestAccess: false,
        loading: false,
        user: {},
      },
      reports: {
        year: 2020,
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(wrapper.find(Welcome)).toExist()
  })
})
