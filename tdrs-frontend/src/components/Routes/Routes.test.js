import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter } from 'react-router-dom'

import Routes from './Routes'

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
    expect(
      screen.getByText('Work Participation Rate and Time Limit Reports')
    ).toBeInTheDocument()
  })
})
