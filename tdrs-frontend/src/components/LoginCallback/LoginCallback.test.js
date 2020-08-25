import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { MemoryRouter, Redirect, Route } from 'react-router-dom'
import * as Alert from '../../actions/alert'
import { ALERT_INFO } from '../Notify'
import LoginCallback from '.'

describe('LoginCallback.js', () => {
  const mockStore = configureStore([thunk])

  it('redirects to "/dashboard" when user is already authenticated', () => {
    const store = mockStore({
      auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <LoginCallback />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper).toContainReact(<Redirect to="/dashboard" />)
  })

  it('redirects to "/" when user not authenticated', () => {
    const store = mockStore({ auth: { authenticated: false } })
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <LoginCallback />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper).toContainReact(<Redirect to="/" />)
  })

  it('alerts a loading message when log-in is in process, does not render child content', () => {
    const store = mockStore({ auth: { loading: true } })
    const spy = jest.spyOn(Alert, 'setAlert')
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
          <LoginCallback />
        </MemoryRouter>
      </Provider>
    )
    expect(wrapper.find(Route).exists()).toBeFalsy()
    expect(spy).toHaveBeenCalledWith({
      heading: 'Please wait...',
      type: ALERT_INFO,
    })
    spy.mockRestore()
  })
})
