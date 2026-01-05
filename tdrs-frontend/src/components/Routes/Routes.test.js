import React from 'react'
import { render, screen } from '@testing-library/react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter } from 'react-router-dom'

import Routes from './Routes'

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
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/IdontExist']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText(/page not found/i)).toBeInTheDocument()
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
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(screen.getByText(/Sign into TANF Data Portal/i)).toBeInTheDocument()
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
    render(
      <Provider store={store}>
        <MemoryRouter>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(screen.getByText(/Welcome to TDP/i)).toBeInTheDocument()
  })
})
