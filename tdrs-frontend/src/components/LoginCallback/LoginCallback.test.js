import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import * as Alert from '../../actions/alert'
import { ALERT_INFO } from '../Alert'
import LoginCallback from '.'
import PrivateRoute from '../PrivateRoute'
import Welcome from '../Welcome'
import SplashPage from '../SplashPage'
import { render, screen } from '@testing-library/react'

describe('LoginCallback.js', () => {
  const mockStore = configureStore([thunk])

  it('redirects to "/welcome" when user is already authenticated', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login', '/']}>
          <Routes>
            <Route exact path="/" element={<SplashPage />} />
            <Route exact path="/login" element={<LoginCallback />} />
            <Route
              exact
              path="/welcome"
              element={
                <PrivateRoute title="Welcome to TDP">
                  <Welcome />
                </PrivateRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText('Welcome to TDP')).toBeInTheDocument()
  })

  it('redirects to "/" when user not authenticated', () => {
    const store = mockStore({ auth: { authenticated: false } })

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login', '/']}>
          <Routes>
            <Route exact path="/" element={<SplashPage />} />
            <Route exact path="/login" element={<LoginCallback />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText('Sign into TANF Data Portal')).toBeInTheDocument()
  })

  it('alerts a loading message when log-in is in process, does not render child content', () => {
    const store = mockStore({ auth: { loading: true } })
    const spy = jest.spyOn(Alert, 'setAlert')

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route exact path="/login" element={<LoginCallback />} />
          </Routes>
        </MemoryRouter>
      </Provider>
    )
    expect(
      screen.queryByText('Sign into TANF Data Portal')
    ).not.toBeInTheDocument()

    expect(spy).toHaveBeenCalledWith({
      heading: 'Please wait...',
      type: ALERT_INFO,
    })
    spy.mockRestore()
  })
})
