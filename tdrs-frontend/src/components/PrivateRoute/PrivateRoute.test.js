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
            <Route
              exact
              path="/very-secret-route"
              element={
                <PrivateRoute title="Test">
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

  it('returns children when user is authenticated', () => {
    createWrapper({ auth: { authenticated: true } })
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
})
