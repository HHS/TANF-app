import React from 'react'
import { render } from '@testing-library/react'
import configureStore from 'redux-mock-store'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'

import Footer from './Footer'
import { permissions } from '../Header/developer_permissions'

describe('Footer', () => {
  const unauthenticatedInitialState = {
    router: { location: { pathname: '/profile' } },
    auth: {
      authenticated: false,
    },
  }
  const adminInitialState = {
    router: { location: { pathname: '/profile' } },
    auth: {
      authenticated: true,
      roles: [{ id: 1, name: 'Developer', permissions }],
    },
  }

  const basicAuthenticatedInitialState = {
    router: { location: { pathname: '/profile' } },
    auth: { authenticated: true },
  }
  const mockStore = configureStore([thunk])
  it('renders the children & families logo', () => {
    const store = mockStore(unauthenticatedInitialState)
    const { container } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(container.querySelector('img')).toBeInTheDocument()
  })

  it('renders the privacy policy link as an unauthenticated user', () => {
    const store = mockStore(unauthenticatedInitialState)
    const { getByText } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(getByText('Privacy policy')).toBeInTheDocument()
  })

  it('renders the privacy policy link as an authenticated user', () => {
    const store = mockStore(basicAuthenticatedInitialState)
    const { getByText } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(getByText('Privacy Policy')).toBeInTheDocument()
  })

  it('renders the vulnerability disclosure policy link as an unauthenticated user', () => {
    const store = mockStore(unauthenticatedInitialState)
    const { getByText } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(getByText('Vulnerability Disclosure Policy')).toBeInTheDocument()
    expect(
      getByText('Vulnerability Disclosure Policy').closest('a')
    ).toHaveAttribute(
      'href',
      'https://www.hhs.gov/vulnerability-disclosure-policy/index.html'
    )
  })

  it('renders the vulnerability disclosure policy link as an authenticated user', () => {
    const store = mockStore(basicAuthenticatedInitialState)
    const { getByText } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(getByText('Vulnerability Disclosure Policy')).toBeInTheDocument()
  })

  it('renders the site map link if a user is authenticated', () => {
    const store = mockStore(basicAuthenticatedInitialState)
    const { getByText } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(getByText('Site Map')).toBeInTheDocument()
  })

  it('does not render the sitemap link if a user is not authenticated', () => {
    const store = mockStore(unauthenticatedInitialState)
    const { queryByText } = render(
      <Provider store={store}>
        <Footer />
      </Provider>
    )
    expect(queryByText('Site Map')).not.toBeInTheDocument()
  })
})
