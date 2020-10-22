import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import {Helmet} from 'react-helmet'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import EditProfile from './EditProfile'

describe('EditProfile', () => {
  const initialState = { stts: { stts: [], loading: false } }
  const mockStore = configureStore([thunk])

  it('should have a card with header Request Access', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )
    const h1 = wrapper.find('h1')

    expect(h1).toExist()
    expect(h1.text()).toEqual('Request Access')
  })

  it('should have a page title with Request Access in it',() => {
    const wrapper = mount( <EditProfile />)

    expect(Helmet.peek().title.join("")).toEqual('Request Access - TDP - TANF Data Portal')
  })

  it('should have a first name input', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const nameInput = wrapper.find('#firstName')

    expect(nameInput).toExist()
  })

  it('should have a last name input', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const nameInput = wrapper.find('#lastName')

    expect(nameInput).toExist()
  })

  it('should have a submit button', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const submitBtn = wrapper.find('button[type="submit"]')

    expect(submitBtn).toExist()
  })

  it('should render a list of options based on stts from the store', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        stts: [
          {
            id: 1,
            type: 'state',
            code: 'AL',
            name: 'Alabama',
          },
          {
            id: 2,
            type: 'state',
            code: 'AK',
            name: 'Alaska',
          },
          {
            id: 140,
            type: 'tribe',
            code: 'AK',
            name: 'Aleutian/Pribilof Islands Association, Inc.',
          },
        ],
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const options = wrapper.find('.sttOption')

    expect(options.length).toEqual(3)
  })
})
