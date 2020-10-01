import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { ALERT_INFO, Alert } from '.'

describe('Alert.js', () => {
  const mockStore = configureStore([thunk])

  it('returns an Alert component', () => {
    const store = mockStore({
      alert: {
        show: true,
        type: ALERT_INFO,
        heading: 'Hey, Look at Me!',
        body: 'more details',
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Alert />
      </Provider>
    )
    expect(wrapper.find('.usa-alert')).toExist()
    expect(wrapper.find('h3')).toIncludeText('Hey, Look at Me!')
    expect(wrapper.find('p')).toIncludeText('more details')
  })

  it('returns a "slim" alert if there is no body', () => {
    const store = mockStore({
      alert: {
        show: true,
        type: ALERT_INFO,
        heading: 'Hey, Look at Me!',
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Alert />
      </Provider>
    )

    expect(wrapper.find('.usa-alert--slim')).toExist()
  })

  it('returns nothing if the "show" property is false', () => {
    const store = mockStore({ alert: { show: false } })
    const wrapper = mount(
      <Provider store={store}>
        <Alert />
      </Provider>
    )
    expect(wrapper.find('.usa-alert')).not.toExist()
  })
})
