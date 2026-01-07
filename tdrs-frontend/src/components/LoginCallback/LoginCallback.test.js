import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import * as Alert from '../../actions/alert'
import { ALERT_INFO } from '../Alert'
import LoginCallback from '.'
import PrivateRoute from '../PrivateRoute'
import Home from '../Home'
import SplashPage from '../SplashPage'
import { render, screen } from '@testing-library/react'
import { useRUM } from '../../hooks/useRUM'

jest.mock('../../hooks/useRUM')

const mockSetUserInfo = jest.fn()
beforeEach(() => {
  useRUM.mockReturnValue({
    setUserInfo: mockSetUserInfo,
    traceAsyncUserAction: jest.fn(),
    traceUserAction: jest.fn(),
    logPageView: jest.fn(),
    logUserAction: jest.fn(),
    logError: jest.fn(),
  })
  mockSetUserInfo.mockClear()
})

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'hi@bye.com',
      roles: [],
      access_request: false,
    },
  },
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

describe('LoginCallback.js', () => {
  const mockStore = configureStore([thunk])

  it('redirects to "/home" when user is already authenticated', () => {
    const store = mockStore(initialState)

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login', '/']}>
          <Routes>
            <Route exact path="/" element={<SplashPage />} />
            <Route exact path="/login" element={<LoginCallback />} />
            <Route
              exact
              path="/home"
              element={
                <PrivateRoute title="Welcome to TDP">
                  <Home setInEditMode={jest.fn()} />
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
    const store = mockStore({
      auth: { authenticated: false, loading: false },
      stts: initialState.stts,
    })

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
    const store = mockStore({
      auth: { loading: true },
      stts: initialState.stts,
    })
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

  it('clears alert when authLoading transitions to false', () => {
    const store = mockStore({
      auth: {
        authenticated: true,
        loading: false,
        user: { email: 'test@test.com', roles: [] },
      },
      stts: initialState.stts,
    })
    const spy = jest.spyOn(Alert, 'clearAlert')

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route exact path="/login" element={<LoginCallback />} />
            <Route exact path="/home" element={<div>Home</div>} />
          </Routes>
        </MemoryRouter>
      </Provider>
    )

    expect(spy).toHaveBeenCalled()
    spy.mockRestore()
  })

  it('calls setUserInfo when user is authenticated', () => {
    const user = { email: 'test@test.com', roles: [] }
    const store = mockStore({
      auth: {
        authenticated: true,
        loading: false,
        user,
      },
      stts: initialState.stts,
    })

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/login']}>
          <Routes>
            <Route exact path="/login" element={<LoginCallback />} />
            <Route exact path="/home" element={<div>Home</div>} />
          </Routes>
        </MemoryRouter>
      </Provider>
    )

    expect(mockSetUserInfo).toHaveBeenCalledWith(user)
  })
})
