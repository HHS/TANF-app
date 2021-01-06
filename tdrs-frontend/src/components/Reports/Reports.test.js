import React from 'react'
import { mount } from 'enzyme'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import Reports from './Reports'
import Button from '../Button'

describe('Reports', () => {
  const initialState = {
    reports: {
      file: null,
      error: null,
      year: 2020,
    },
  }
  const mockStore = configureStore([thunk])

  it('should render the USWDS Select component with two options', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = wrapper.find('.usa-select')

    expect(select).toExist()

    const options = wrapper.find('option')

    expect(options.length).toEqual(2)
  })

  it('should change route to `/reports/:year/upload` on click of `Begin Report` button', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const beginButton = wrapper.find(Button)

    expect(beginButton).toExist()

    beginButton.simulate('click')

    expect(window.location.href.includes('/reports/2020/upload')).toBeTruthy()
  })

  it('should dispatch setYear when a year is selcted', () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)
    const wrapper = mount(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        value: 2021,
      },
    })

    expect(store.dispatch).toHaveBeenCalledTimes(1)
  })
})
