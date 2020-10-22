import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'

import EditProfile, { validation } from './EditProfile'

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

  it('should mount a list of options based on stts from the store', () => {
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

    const options = wrapper.find('option')

    expect(options.length).toEqual(4)
  })

  it('should have errors when you try to submit and first name does not have at least 1 character', () => {
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

    const form = wrapper.find('.usa-form').hostNodes()

    form.simulate('submit', {
      preventDefault: () => {},
    })

    const errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)
    expect(errorMessages.first().text()).toEqual('First Name is required')
    expect(errorMessages.at(1).text()).toEqual('Last Name is required')
    expect(errorMessages.last().text()).toEqual('STT is required')
  })

  it('should remove error message when you add a character and blur out of input', () => {
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

    const form = wrapper.find('.usa-form').hostNodes()

    form.simulate('submit', {
      preventDefault: () => {},
    })

    let errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)

    const firstNameInput = wrapper.find('#firstName')

    firstNameInput.simulate('change', {
      target: {
        value: 's',
        name: 'firstName',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(2)

    const lastNameInput = wrapper.find('#lastName')

    lastNameInput.simulate('change', {
      target: {
        value: 's',
        name: 'lastName',
      },
    })

    lastNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(1)

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        value: 'alaska',
        name: 'stt',
      },
    })

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(0)
  })

  it("should return 'First Name is required' if fieldName is firstName and fieldValue is empty", () => {
    const error = validation('firstName', '')

    expect(error).toEqual('First Name is required')
  })

  it("should return 'Last Name is required' if fieldName is lastName and fieldValue is empty", () => {
    const error = validation('lastName', '')

    expect(error).toEqual('Last Name is required')
  })

  it("should return 'STT is required' if fieldName is firstName and fieldValue is empty", () => {
    const error = validation('stt', '')

    expect(error).toEqual('STT is required')
  })

  it("should return ' is required' if fieldName is not passed in and fieldValue is empty", () => {
    const error = validation('', '')

    expect(error).toEqual(' is required')
  })

  it('should return null if fieldValue is not empty', () => {
    const error = validation('firstName', 'peter')

    expect(error).toEqual(null)
  })

  it('should display an error message when the input has` been touched', () => {
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

    const form = wrapper.find('.usa-form').hostNodes()

    form.simulate('submit', {
      preventDefault: () => {},
    })

    let errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)

    const firstNameInput = wrapper.find('#firstName')

    firstNameInput.simulate('change', {
      target: {
        name: 'firstName',
        value: 's',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(2)

    firstNameInput.simulate('change', {
      target: {
        name: 'firstName',
        value: '',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)
  })
})
