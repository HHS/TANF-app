import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'

import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import App from './App'

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
  }
  const mockStore = configureStore([thunk])

  beforeEach(() => {
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { pathname: '/' },
    })
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

  it('renders sticky button at bottom right of Apps viewport', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <MemoryRouter>
          <App />
        </MemoryRouter>
      </Provider>
    )
    expect(screen.getByText('Give Feedback')).toBeInTheDocument()
  })

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
})
