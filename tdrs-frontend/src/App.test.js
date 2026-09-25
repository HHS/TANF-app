import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import * as reactRedux from 'react-redux'
import { MemoryRouter } from 'react-router'

import App from './App'
import { fetchSttList } from './actions/sttList'

jest.mock('react-redux', () => {
  const actual = jest.requireActual('react-redux')
  return { ...actual, useDispatch: jest.fn() }
})

jest.mock('./actions/sttList', () => ({
  fetchSttList: jest.fn(() => ({ type: 'FETCH_STTS' })),
}))

jest.mock('jest-transform-stub', () => require('./__mocks__/svg'))

describe('App.js', () => {
  const initialState = {
    alert: {
      show: false,
      type: null,
      heading: null,
      body: null,
    },
    router: {
      location: {
        pathname: '/',
      },
    },
    auth: {
      user: null,
    },
    feedbackWidget: {
      isOpen: false,
      lockedDataType: null,
    },
    stts: {
      sttList: [],
      loading: true,
    },
  }
  const mockStore = configureStore([thunk])

  beforeEach(() => {
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { pathname: '/' },
    })
    reactRedux.useDispatch.mockReturnValue(jest.fn())
    fetchSttList.mockClear()
  })

  afterEach(() => {
    window.location.href = ''
  })

  it('renders the Gov Banner', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText(/official website/i)).toBeInTheDocument()
  })

  it('renders the Header', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText('TANF Data Portal')).toBeInTheDocument()
  })

  it('renders the Alert', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    // Alert component is rendered but hidden when show is false
    const alertContainer = container.querySelector('.usa-alert')
    // When show is false, no alert is rendered
    expect(alertContainer).not.toBeInTheDocument()
  })

  it('hides feedback on the public landing page', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.queryByText('Give Feedback')).not.toBeInTheDocument()
    expect(screen.queryByTestId('feedback-form')).not.toBeInTheDocument()
  })

  it.each(['Initial', 'Access request', 'Pending', 'Denied', 'Deactivated'])(
    'hides feedback for a logged-in user with %s status',
    (accountStatus) => {
      const store = mockStore({
        ...initialState,
        auth: {
          authenticated: true,
          user: { account_approval_status: accountStatus, roles: [] },
        },
      })
      render(
        <Provider store={store}>
          <MemoryRouter>
            <App />
          </MemoryRouter>
        </Provider>
      )
      expect(screen.queryByText('Give Feedback')).not.toBeInTheDocument()
    }
  )

  it.each(['login.gov', 'AMS'])(
    'shows feedback after %s login and removes an open form on logout',
    (loginProvider) => {
      const user = {
        account_approval_status: 'Approved',
        roles: [],
        login_gov_uuid: loginProvider === 'login.gov' ? 'test-user' : null,
        hhs_id: loginProvider === 'AMS' ? 'test-user' : null,
      }
      const renderApp = (authenticated) => (
        <Provider
          store={mockStore({
            ...initialState,
            auth: { authenticated, user },
          })}
        >
          <MemoryRouter>
            <App />
          </MemoryRouter>
        </Provider>
      )
      const { rerender } = render(renderApp(false))
      expect(screen.queryByText('Give Feedback')).not.toBeInTheDocument()

      rerender(renderApp(true))
      fireEvent.click(screen.getByRole('button', { name: 'Give Feedback' }))
      expect(screen.getByTestId('feedback-form')).toBeInTheDocument()
      expect(screen.getByLabelText('Send anonymously')).toBeInTheDocument()

      rerender(renderApp(false))
      expect(screen.queryByText('Give Feedback')).not.toBeInTheDocument()
      expect(screen.queryByTestId('feedback-form')).not.toBeInTheDocument()

      rerender(renderApp(true))
      expect(screen.getByText('Give Feedback')).toBeInTheDocument()
      expect(screen.queryByTestId('feedback-form')).not.toBeInTheDocument()
    }
  )

  it.each(['/data-files', '/fra-data-files'])(
    'hides an open upload feedback widget after logout on %s',
    (pathname) => {
      window.location.pathname = pathname
      const renderApp = (authenticated) => (
        <Provider
          store={mockStore({
            ...initialState,
            auth: {
              authenticated,
              user: { account_approval_status: 'Approved', roles: [] },
            },
            feedbackWidget: { isOpen: true, dataType: 'tanf' },
          })}
        >
          <MemoryRouter>
            <App />
          </MemoryRouter>
        </Provider>
      )
      const { rerender } = render(renderApp(true))
      expect(screen.getByTestId('feedback-widget')).toBeInTheDocument()

      rerender(renderApp(false))
      expect(screen.queryByTestId('feedback-widget')).not.toBeInTheDocument()
      expect(screen.queryByTestId('feedback-form')).not.toBeInTheDocument()
    }
  )

  it('renders skip link with correct href and text', () => {
    const store = mockStore(initialState)

    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )

    const skipLink = screen.getByText('Skip to main content')
    expect(skipLink).toBeInTheDocument()
    expect(skipLink).toHaveAttribute('href', '#main-content')
  })

  it('should redirect to #main-content when space bar is pressed on "skip links" element', () => {
    const url = '#main-content'
    const initialUrl = '#before'

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: initialUrl,
      },
    })

    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )

    const skipLink = screen.getByText('Skip to main content')
    fireEvent.keyPress(skipLink, {
      charCode: 32,
    })

    expect(window.location.href).toEqual(url)
  })

  it('should do nothing if any key besides space bar is pressed', () => {
    const url = ''

    global.window = Object.create(window)
    Object.defineProperty(window, 'location', {
      value: {
        href: url,
      },
    })

    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )

    const skipLink = screen.getByText('Skip to main content')
    fireEvent.keyPress(skipLink, {
      charCode: 25,
    })

    expect(window.location.href).toEqual(url)
  })

  it('should not show modal initially', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    const feedbackModal = screen.queryByRole('dialog', { name: /feedback/i })
    expect(feedbackModal).not.toBeInTheDocument()
  })

  it('dispatches fetchSttList when user is present', async () => {
    const store = mockStore({
      ...initialState,
      auth: {
        user: { id: 1, email: 'user@example.com', roles: [] },
      },
    })

    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )

    await waitFor(() => {
      expect(fetchSttList).toHaveBeenCalled()
    })
  })
})
