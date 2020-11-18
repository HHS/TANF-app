/* eslint-disable no-param-reassign */
import React from 'react'
import thunk from 'redux-thunk'
import { mount, shallow } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Route } from 'react-router-dom'
import * as Alert from '../../actions/alert'

import PrivateRoute from '.'

describe('PrivateRoute.js', () => {
  const mockStore = configureStore([thunk])

  const createWrapper = (storeOptions) =>
    mount(
      <Provider store={mockStore(storeOptions)}>
        <MemoryRouter initialEntries={['/very-secret-route']}>
          <PrivateRoute title="Test" path="/very-secret-route">
            <Route>Hello Private Content</Route>
          </PrivateRoute>
        </MemoryRouter>
      </Provider>
    )

  it('does not return children when user is not authenticated', () => {
    const wrapper = createWrapper({ auth: { authenticated: false } })
    expect(wrapper.find(Route).exists()).toBeFalsy()
  })

  it('returns children when user is authenticated', () => {
    const wrapper = createWrapper({ auth: { authenticated: true } })
    expect(wrapper.find(Route)).toExist()
  })

  it('should should not render h1 if not authenticated', () => {
    const wrapper = createWrapper({ auth: { authenticated: false } })

    const h1 = wrapper.find('h1')
    expect(h1.exists()).toBeFalsy()
  })

  it('should render an h1 with the title if user is authenticated', () => {
    const wrapper = createWrapper({ auth: { authenticated: true } })
    const h1 = wrapper.find('h1')

    expect(h1).toExist()
    expect(h1.text()).toEqual('Test')
  })

  it('alerts a loading message when log-in is in process, does not render child content', () => {
    const spy = jest.spyOn(Alert, 'setAlert')
    const wrapper = createWrapper({ auth: { loading: true } })
    expect(wrapper.find(Route).exists()).toBeFalsy()
    expect(spy).toHaveBeenCalledWith({
      heading: 'Please wait...',
      type: 'info',
    })
    spy.mockRestore()
  })
})
