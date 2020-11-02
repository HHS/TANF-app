import React from 'react'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { fireEvent, render } from '@testing-library/react'

import { MemoryRouter, Redirect } from 'react-router-dom'
import EditProfile, { validation } from './EditProfile'
import { fetchSttList } from '../../actions/sttList'

describe('EditProfile', () => {
  const initialState = {
    auth: { authenticated: true, user: { email: 'hi@bye.com' } },
    stts: { sttList: [], loading: false },
    requestAccess: {
      requestAccess: false,
      loading: false,
      user: {},
    },
  }
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

  it('should set firstName state value to equal the input value', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const input = container.querySelector('input[name="firstName"]')

    fireEvent.change(input, {
      target: { value: 'Peter' },
    })

    expect(input.value).toEqual('Peter')
  })

  it('should set lastName state value to equal the input value', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const input = container.querySelector('input[name="lastName"]')

    fireEvent.change(input, {
      target: { value: 'Parker' },
    })

    expect(input.value).toEqual('Parker')
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
        sttList: [
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
        sttList: [
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

    expect(errorMessages.length).toEqual(4)
    expect(errorMessages.at(1).text()).toEqual('First Name is required')
    expect(errorMessages.at(2).text()).toEqual('Last Name is required')
    expect(errorMessages.last().text()).toEqual(
      'A state, tribe, or territory is required'
    )
  })

  it('should remove error message when you add a character and blur out of input', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        sttList: [
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

    expect(errorMessages.length).toEqual(4)

    const firstNameInput = wrapper.find('#firstName')

    firstNameInput.simulate('change', {
      target: {
        value: 's',
        name: 'firstName',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)

    const lastNameInput = wrapper.find('#lastName')

    lastNameInput.simulate('change', {
      target: {
        value: 's',
        name: 'lastName',
      },
    })

    lastNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(2)
    expect(errorMessages.first().hasClass('display-none')).toEqual(false)

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        value: 'alaska',
        name: 'stt',
      },
    })

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(1)
    expect(errorMessages.first().hasClass('display-none')).toEqual(true)
  })

  it("should return 'First Name is required' if fieldName is firstName and fieldValue is empty", () => {
    const error = validation('firstName', '')

    expect(error).toEqual('First Name is required')
  })

  it("should return 'Last Name is required' if fieldName is lastName and fieldValue is empty", () => {
    const error = validation('lastName', '')

    expect(error).toEqual('Last Name is required')
  })

  it("should return 'A state, tribe, or territory is required' if fieldName is firstName and fieldValue is empty", () => {
    const error = validation('stt', '')

    expect(error).toEqual('A state, tribe, or territory is required')
  })

  it("should return ' is required' if fieldName is not passed in and fieldValue is empty", () => {
    const error = validation('', '')

    expect(error).toEqual(' is required')
  })

  it('should return null if fieldValue is not empty', () => {
    const error = validation('firstName', 'peter')

    expect(error).toEqual(null)
  })

  it('should display an error message when the input has been touched', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        sttList: [
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

    expect(errorMessages.length).toEqual(4)

    const firstNameInput = wrapper.find('#firstName')

    firstNameInput.simulate('change', {
      target: {
        name: 'firstName',
        value: 's',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)

    firstNameInput.simulate('change', {
      target: {
        name: 'firstName',
        value: '',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(4)
  })

  it('should set the Select element value to the value of the event when there is a selected stt', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        sttList: [
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

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: { value: 'alaska' },
    })

    expect(select.instance().value).toEqual('alaska')
  })

  it('should reset Select element value to an empty string when there is no selected stt', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        sttList: [
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

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: { value: '' },
    })

    expect(select.instance().value).toEqual('')
  })

  it('should reset Select element value to an empty string when there is no stt that matches the value passed in', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        sttList: [
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

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: { value: 'colorado' },
    })

    expect(select.instance().value).toEqual('')
  })

  it('routes "/edit-profile" to the Unassigned page when user has requested access', () => {
    const store = mockStore({
      ...initialState,
      requestAccess: {
        ...initialState.requestAccess,
        requestAccess: true,
      },
      stts: {
        sttList: [
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
        <MemoryRouter>
          <EditProfile />
        </MemoryRouter>
      </Provider>
    )

    expect(wrapper).toContainReact(<Redirect to="/unassigned" />)
  })

  it('should dispatch "requestAccess" when form is submitted', () => {
    const store = mockStore({
      ...initialState,
      stts: {
        sttList: [
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
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)
    const wrapper = mount(
      <Provider store={store}>
        <EditProfile />
      </Provider>
    )

    const firstNameInput = wrapper.find('#firstName')
    firstNameInput.simulate('change', {
      target: { value: 'harry', name: 'firstName' },
    })

    const lastNameInput = wrapper.find('#lastName')
    lastNameInput.simulate('change', {
      target: { name: 'lastName', value: 'potter' },
    })

    const select = wrapper.find('.usa-select')
    select.simulate('change', {
      target: { name: 'stt', value: 'alaska' },
    })

    expect(store.dispatch).toHaveBeenCalledTimes(1)

    const form = wrapper.find('.usa-form').hostNodes()
    form.simulate('submit', {
      preventDefault: () => {},
    })

    expect(store.dispatch).toHaveBeenCalledTimes(2)
  })
})
