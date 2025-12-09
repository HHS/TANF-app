import React from 'react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import SplashPage from './SplashPage'
import { render, screen, fireEvent } from '@testing-library/react'
import PrivateRoute from '../PrivateRoute'
import Home from '../Home'

const initialState = {
  auth: { authenticated: false, inactive: false },
  stts: {
    loading: false,
    sttList: [
      {
        id: 1,
        type: 'state',
        code: 'AL',
        name: 'Alabama',
      },
      {
        id: 2,
        type: 'state',
        code: 'AK',
        name: 'Alaska',
      },
      {
        id: 140,
        type: 'tribe',
        code: 'AK',
        name: 'Aleutian/Pribilof Islands Association, Inc.',
      },
    ],
  },
}
const mockStore = configureStore([thunk])

describe('SplashPage', () => {
  beforeEach(() => {
    jest.spyOn(global.Math, 'random').mockReturnValue(0)
  })

  afterEach(() => {
    jest.spyOn(global.Math, 'random').mockRestore()
  })

  it('renders a sign in header', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    const hero = container.querySelector('.usa-hero__callout')
    expect(hero.querySelector('h1')).toHaveTextContent(
      'Sign into TANF Data Portal'
    )
  })

  it('does not render the page while auth is loading', () => {
    const store = mockStore({ auth: { loading: true } })
    render(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    expect(screen.queryByText('SplashPage to TDRS!')).not.toBeInTheDocument()
  })

  it('renders an Inactive Account alert if the user authenticates with an inactive account', () => {
    const store = mockStore({
      auth: { authenticated: false, inactive: true },
    })
    const { container } = render(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    const alert = container.querySelector('.usa-alert--error')
    expect(alert.querySelector('h3')).toHaveTextContent('Inactive Account')
  })

  it('redirects to API login endpoint when login.gov sign-in button is clicked', () => {
    const store = mockStore(initialState)

    const url = 'http://localhost:8080/v1/login/dotgov'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    render(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    const button = screen.getByRole('button', {
      name: /Sign in with.*Login\.gov.*for grantees/i,
    })
    fireEvent.click(button)
    expect(window.location.href).toEqual(url)
  })

  it('redirects to API login endpoint when ACF AMS sign-in button is clicked', () => {
    const store = mockStore(initialState)

    const url = 'http://localhost:8080/v1/login/ams'
    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    render(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    const button = screen.getByRole('button', {
      name: /Sign in with ACF AMS for ACF staff/i,
    })
    fireEvent.click(button)
    expect(window.location.href).toEqual(url)
  })

  it('redirects to /home when user is already authenticated', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        user: { email: 'hi@bye.com' },
      },
      stts: initialState.stts,
    })
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/home', '/']}>
          <Routes>
            <Route
              exact
              path="/home"
              element={
                <PrivateRoute title="Welcome to TDP">
                  <Home setInEditMode={jest.fn()} />
                </PrivateRoute>
              }
            />
            <Route exact path="/" element={<SplashPage />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText('Welcome to TDP')).toBeInTheDocument()
  })

  it('changes the background image on every render', async () => {
    // Render the SplashPage
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )

    const hero = container.getElementsByClassName('usa-hero')[0]
    expect(hero).toHaveClass('usa-hero1')
  })
})
