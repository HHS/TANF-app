/* eslint-disable no-param-reassign */
import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { render, screen } from '@testing-library/react'

import * as Alert from '../../actions/alert'

import PrivateRoute from '.'

describe('PrivateRoute.js', () => {
  const mockStore = configureStore([thunk])

  const createWrapper = (storeOptions) =>
    render(
      <Provider store={mockStore(storeOptions)}>
        <MemoryRouter initialEntries={['/very-secret-route']}>
          <Routes>
            <Route exect path="/home" element={<p>hello, world</p>} />
            <Route
              exact
              path="/very-secret-route"
              element={
                <PrivateRoute title="Test" requiredPermissions={['can_view']}>
                  <p>Hello Private Content</p>
                </PrivateRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </Provider>
    )

  it('does not return children when user is not authenticated', () => {
    createWrapper({ auth: { authenticated: false } })
    expect(screen.queryByText('Hello Private Content')).not.toBeInTheDocument()
  })

  it('returns children when user is authenticated and has required permissions', () => {
    createWrapper({
      auth: {
        authenticated: true,
        user: {
          roles: [{ permissions: [{ codename: 'can_view' }] }],
        },
      },
    })
    expect(screen.queryByText('Hello Private Content')).toBeInTheDocument()
  })

  it('alerts a loading message when log-in is in process, does not render child content', () => {
    const spy = jest.spyOn(Alert, 'setAlert')
    createWrapper({ auth: { loading: true } })
    expect(screen.queryByText('Hello Private Content')).not.toBeInTheDocument()
    expect(spy).toHaveBeenCalledWith({
      heading: 'Please wait...',
      type: 'info',
    })
    spy.mockRestore()
  })

  it('redirects to home when the user does not have the required permissions', () => {
    createWrapper({
      auth: {
        authenticated: true,
        user: {
          roles: [{ permissions: [{ codename: 'some_stuff' }] }],
        },
      },
    })

    expect(screen.queryByText('Hello Private Content')).not.toBeInTheDocument()
    expect(screen.queryByText('hello, world')).toBeInTheDocument()
  })
})
