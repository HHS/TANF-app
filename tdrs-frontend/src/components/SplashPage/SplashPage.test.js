import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import SplashPage from './SplashPage'
import { render, screen } from '@testing-library/react'
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

  it('renders an Inactive Account alert if the user authenticates with an inactive account', () => {
    const store = mockStore({
      auth: { authenticated: false, inactive: true },
    })
    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    const alert = wrapper.find('.usa-alert--error')
    expect(alert.find('h3')).toIncludeText('Inactive Account')
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

    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    wrapper.find('#loginDotGovSignIn').simulate('click', {
      preventDefault: () => {},
    })
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

    const wrapper = mount(
      <Provider store={store}>
        <SplashPage />
      </Provider>
    )
    wrapper.find('#acfAmsSignIn').simulate('click', {
      preventDefault: () => {},
    })
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
                  <Home />
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
