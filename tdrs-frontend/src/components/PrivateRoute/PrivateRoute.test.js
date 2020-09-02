/* eslint-disable no-param-reassign */
import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route } from 'react-router-dom'
import * as Alert from '../../actions/alert'

import PrivateRoute from '.'

describe('PrivateRoute.js', () => {
  const mockStore = configureStore([thunk])

  it('does not return children when user is not authenticated', () => {
    const store = mockStore({ auth: { authenticated: false } })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <PrivateRoute path="/very-secret-route">
            <Route>Hello Private Content</Route>
          </PrivateRoute>
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(Route).exists()).toBeFalsy()
  })

  it('returns children when user is authenticated', () => {
    const store = mockStore({ auth: { authenticated: true } })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <PrivateRoute path="/very-secret-route">
            <Route>Hello Private Content</Route>
          </PrivateRoute>
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(Route)).toExist()
  })

  it('alerts a loading message when log-in is in process, does not render child content', () => {
    const store = mockStore({ auth: { loading: true } })
    const spy = jest.spyOn(Alert, 'setAlert')
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <PrivateRoute path="/very-secret-route">
            <Route>Hello Private Content</Route>
          </PrivateRoute>
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(Route).exists()).toBeFalsy()
    expect(spy).toHaveBeenCalledWith({
      heading: 'Please wait...',
      type: 'info',
    })
    spy.mockRestore()
  })
})
