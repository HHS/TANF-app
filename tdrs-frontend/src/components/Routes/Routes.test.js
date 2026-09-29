import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, useLocation } from 'react-router-dom'

import Routes from './Routes'

const CurrentLocation = () => {
  const { pathname, search, hash } = useLocation()
  return <output data-testid="location">{`${pathname}${search}${hash}`}</output>
}

let mockHomeEditMode = false
let mockProfileEditMode = false

jest.mock('../Home', () => {
  const React = require('react')
  return function MockHome({ setInEditMode }) {
    React.useEffect(() => {
      if (mockHomeEditMode) {
        setInEditMode(true)
      }
    }, [setInEditMode])
    return <div>Home</div>
  }
})

jest.mock('../Profile', () => {
  const React = require('react')
  return function MockProfile({ onEdit }) {
    React.useEffect(() => {
      if (mockProfileEditMode && onEdit) {
        onEdit()
      }
    }, [onEdit])
    return <div>Profile</div>
  }
})

jest.mock('../Reports', () => {
  const React = require('react')
  return {
    __esModule: true,
    default: () => <div>Reports</div>,
    FRAReports: () => <div>FRA Reports</div>,
  }
})

jest.mock('../FeedbackReports/FeedbackReports', () => {
  const React = require('react')
  return function MockFeedbackReports() {
    return <div>Feedback Reports</div>
  }
})

jest.mock('../SiteMap', () => {
  const React = require('react')
  return function MockSiteMap() {
    return <div>Site Map</div>
  }
})

describe('Routes.js', () => {
  const mockStore = configureStore([thunk])

  const makeState = ({ authUser } = {}) => ({
    auth: {
      authenticated: true,
      loading: false,
      user: authUser,
    },
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

  beforeEach(() => {
    mockHomeEditMode = false
    mockProfileEditMode = false
  })

  describe('login destinations', () => {
    const destination =
      '/data-files/2026/1/tanf/1/history?type=tanf&filter=a%2Bb#results'
    const approvedUser = {
      email: 'grantee@example.com',
      account_approval_status: 'Approved',
      roles: [],
      permissions: [
        { codename: 'view_datafile' },
        { codename: 'add_datafile' },
      ],
    }

    const renderEntry = (entry, auth = {}) => {
      const state = makeState({ authUser: approvedUser })
      const store = mockStore({ ...state, auth: { ...state.auth, ...auth } })
      return render(
        <React.StrictMode>
          <Provider store={store}>
            <MemoryRouter initialEntries={[entry]}>
              <Routes />
              <CurrentLocation />
            </MemoryRouter>
          </Provider>
        </React.StrictMode>
      )
    }

    it.each(['/data-files?type=tanf', destination, '/profile#contact'])(
      'opens %s directly for authenticated users',
      (entry) => {
        renderEntry(entry)
        expect(screen.getByTestId('location')).toHaveTextContent(entry)
      }
    )

    describe.each([
      ['legacy', '/v1', '/login'],
      ['Keycloak', '/v2', '/'],
      ['canary legacy', '', '/login'],
      ['canary Keycloak', '', '/'],
    ])('%s authentication', (flow, authPath, callback) => {
      it.each([
        ['Login.gov', /Sign in with.*Login\.gov.*for grantees/i, 'dotgov'],
        ['AMS', /Sign in with ACF AMS for ACF staff/i, 'ams'],
      ])(
        'restores the requested URL after %s sign-in',
        (provider, button, idp) => {
          const originalLocation = window.location
          const originalAuthUrl = process.env.REACT_APP_AUTH_URL
          const authUrl = `https://tdp.example.com${authPath}`
          process.env.REACT_APP_AUTH_URL = authUrl
          Object.defineProperty(window, 'location', {
            configurable: true,
            value: {
              origin: originalLocation.origin,
              href: originalLocation.href,
            },
          })

          try {
            const initialVisit = renderEntry(destination, {
              authenticated: false,
            })
            expect(
              screen.getByText('Sign into TANF Data Portal')
            ).toBeInTheDocument()
            expect(screen.queryByText('Reports')).not.toBeInTheDocument()
            expect(screen.getByTestId('location').textContent).toBe(
              `/?${new URLSearchParams({ next: destination })}`
            )
            initialVisit.unmount()

            // A refresh before sign-in must not lose the destination.
            const refreshedVisit = renderEntry(
              `/?${new URLSearchParams({ next: destination })}`,
              { authenticated: false }
            )
            fireEvent.click(screen.getByRole('button', { name: button }))
            expect(window.location.href).toBe(
              `${authUrl}/login/${idp}?${new URLSearchParams({ next: destination })}`
            )
            refreshedVisit.unmount()

            // The IdP returns to a fresh app instance with an authenticated session.
            const signedInVisit = renderEntry(destination)
            expect(screen.getByText('Reports')).toBeInTheDocument()
            expect(screen.getByTestId('location')).toHaveTextContent(
              destination
            )
            signedInVisit.unmount()

            renderEntry(callback)
            expect(screen.getByTestId('location')).toHaveTextContent('/home')
          } finally {
            Object.defineProperty(window, 'location', {
              value: originalLocation,
            })
            if (originalAuthUrl === undefined) {
              delete process.env.REACT_APP_AUTH_URL
            } else {
              process.env.REACT_APP_AUTH_URL = originalAuthUrl
            }
          }
        }
      )
    })

    it('waits for authentication before leaving the requested page', () => {
      renderEntry(destination, { authenticated: false, loading: true })
      expect(screen.getByTestId('location')).toHaveTextContent(destination)
    })

    it.each(['/', '/login'])(
      'waits for authentication on %s before restoring a destination',
      (callback) => {
        const callbackUrl = `${callback}?${new URLSearchParams({ next: destination })}`
        const pendingVisit = renderEntry(callbackUrl, { loading: true })
        expect(screen.getByTestId('location').textContent).toBe(callbackUrl)
        expect(screen.queryByText('Reports')).not.toBeInTheDocument()
        pendingVisit.unmount()

        renderEntry(callbackUrl)
        expect(screen.getByTestId('location')).toHaveTextContent(destination)
      }
    )

    it('preserves the destination after a failed login so the user can retry', () => {
      const callback = `/login?${new URLSearchParams({ next: destination })}`
      const failedVisit = renderEntry(callback, { authenticated: false })
      expect(screen.getByText('Sign into TANF Data Portal')).toBeInTheDocument()
      failedVisit.unmount()

      renderEntry(callback)
      expect(screen.getByTestId('location')).toHaveTextContent(destination)
    })

    it.each([
      { ...approvedUser, permissions: [] },
      { ...approvedUser, account_approval_status: 'Pending' },
    ])('enforces page access after sign-in for user %j', (user) => {
      renderEntry(destination, { user })
      expect(screen.getByTestId('location')).toHaveTextContent('/home')
      expect(screen.queryByText('Reports')).not.toBeInTheDocument()
    })

    it('sends ACF OCIO users to the admin site regardless of the destination', () => {
      const originalLocation = window.location
      Object.defineProperty(window, 'location', {
        configurable: true,
        writable: true,
        value: originalLocation,
      })

      try {
        renderEntry('/login', { user: { roles: [{ name: 'ACF OCIO' }] } })
        expect(window.location).toBe(
          `${process.env.REACT_APP_BACKEND_HOST}/admin/`
        )
        expect(screen.queryByText('Reports')).not.toBeInTheDocument()
      } finally {
        Object.defineProperty(window, 'location', { value: originalLocation })
      }
    })
  })

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

  it('uses "Request Submitted" title when user account is in review', () => {
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Pending',
          roles: [],
          permissions: [],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/home']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.getByRole('heading', { name: 'Request Submitted' })
    ).toBeInTheDocument()
  })

  it('uses "Edit Access Request" title when edit mode is enabled for home', async () => {
    mockHomeEditMode = true
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Pending',
          roles: [],
          permissions: [],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/home']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Edit Access Request' })
      ).toBeInTheDocument()
    })
  })

  it('uses "My Profile" title when profile is not in edit mode', () => {
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Approved',
          roles: [],
          permissions: [],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/profile']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.getByRole('heading', { name: 'My Profile' })
    ).toBeInTheDocument()
  })

  it('uses "Edit Profile" title when profile is in edit mode', async () => {
    mockProfileEditMode = true
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Approved',
          roles: [{ name: 'OFA System Admin', permissions: [] }],
          permissions: [],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/profile']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Edit Profile' })
      ).toBeInTheDocument()
    })
  })

  it('uses "Edit Access Request" title when profile is in edit mode and account is in review', async () => {
    mockProfileEditMode = true
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Pending',
          roles: [],
          permissions: [],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/profile']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: 'Edit Access Request' })
      ).toBeInTheDocument()
    })
  })

  it('uses upload feedback reports title and subtitle when user can upload', () => {
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Approved',
          roles: [],
          permissions: [
            { codename: 'view_reportfile' },
            { codename: 'view_reportsource' },
            { codename: 'add_reportsource' },
          ],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/feedback-reports']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.getByRole('heading', { name: 'Upload Feedback Reports' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'TANF WPR, SSP WPR, TANF & SSP Combined, and Time Limit Reports'
      )
    ).toBeInTheDocument()
  })

  it('uses view feedback reports title and subtitle when user cannot upload', () => {
    const store = mockStore(
      makeState({
        authUser: {
          account_approval_status: 'Approved',
          roles: [],
          permissions: [{ codename: 'view_reportfile' }],
        },
      })
    )
    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/feedback-reports']}>
          <Routes />
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.getByRole('heading', { name: 'Feedback Reports' })
    ).toBeInTheDocument()
    // STT view should not have a subtitle
    expect(
      screen.queryByText('Work Participation Rate and Time Limit Reports')
    ).not.toBeInTheDocument()
  })
})
