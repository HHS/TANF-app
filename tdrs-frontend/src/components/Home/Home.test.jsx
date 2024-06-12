import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import { mount } from 'enzyme'
import Home from '../Home'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import PrivateRoute from '../PrivateRoute'

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'hi@bye.com',
      roles: [],
      access_request: false, // !! buncha uses throughout
      account_approval_status: 'Initial',
    },
  },
  stts: {
    loading: false,
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
}

describe('Home', () => {
  const mockStore = configureStore([thunk])

  it('should render the Home page with the request access subheader', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [],
          access_request: false,
          account_approval_status: 'Access request',
        },
      },
    })
    const { getByText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const header = getByText(
      `Your request for access is currently being reviewed by an OFA Admin. We'll send you an email when it's been approved.`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the Home page with the user's current role", () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 1, name: 'OFA Admin', permission: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const header = getByText(
      `You have been approved for access to TDP. For guidance on submitting data, managing your account, and utilizing other functionality please refer to the TDP Knowledge Center.`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the Home page with the user's OFA admin role", () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [{ id: 2, name: 'Data Analyst', permission: [] }],
          access_request: false,
          account_approval_status: 'Approved',
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const header = getByText(
      `You have been approved for access to TDP. For guidance on submitting data, managing your account, and utilizing other functionality please refer to the TDP Knowledge Center.`
    )
    expect(header).toBeInTheDocument()
  })

  it("should render the Home page with the user's Data Analyst role and permissions", () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          access_request: false,
          account_approval_status: 'Approved',
          email: 'hi@bye.com',
          roles: [
            {
              id: 1,
              name: 'Data Analyst',
            },
          ],
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    expect(
      getByText(
        `You have been approved for access to TDP. For guidance on submitting data, managing your account, and utilizing other functionality please refer to the TDP Knowledge Center.`
      )
    ).toBeInTheDocument()
  })
})

describe('Pre-approval Home page', () => {
  const mockStore = configureStore([thunk])

  it('should have a first name input', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const nameInput = wrapper.find('#firstName')

    expect(nameInput).toExist()
  })

  it('should have a last name input', () => {
    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const nameInput = wrapper.find('#lastName')

    expect(nameInput).toExist()
  })

  it('should set firstName state value to equal the input value', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <Home />
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
        <Home />
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
        <Home />
      </Provider>
    )

    const submitBtn = wrapper.find('button[type="submit"]')

    expect(submitBtn).toExist()
  })

  it('should mount a list of stt options based on stts from the store', () => {
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
          {
            id: 1111,
            type: 'territory',
            code: 'G',
            name: 'Guam',
          },
        ],
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const options = wrapper.find('option')

    expect(options.length).toEqual(3)
  })

  it('should mount a list of tribe options based on stts from the store', () => {
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
          {
            id: 1111,
            type: 'territory',
            code: 'G',
            name: 'Guam',
          },
        ],
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const radio = wrapper.find('#tribe')
    radio.simulate('change', {
      target: { name: 'jurisdictionType', value: 'tribe' },
    })

    const options = wrapper.find('option')
    expect(options.length).toEqual(2)
  })

  it('should mount a list of territory options based on stts from the store', () => {
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
          {
            id: 1111,
            type: 'territory',
            code: 'G',
            name: 'Guam',
          },
        ],
      },
    })
    const wrapper = mount(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const radio = wrapper.find('#territory')
    radio.simulate('change', {
      target: { name: 'jurisdictionType', value: 'territory' },
    })

    const options = wrapper.find('option')
    expect(options.length).toEqual(2)
  })

  it('should not show the stt combno box for non-STT users', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'admin@acf.hhs.gov',
          roles: [],
          access_request: false,
        },
      },
    })

    const wrapper = mount(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const options = wrapper.find('option')

    expect(options).toEqual({})
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
    const { getByText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    fireEvent.click(getByText('Request Access'))

    expect(getByText('First Name is required')).toBeInTheDocument()
    expect(getByText('Last Name is required')).toBeInTheDocument()
    expect(getByText('A state is required')).toBeInTheDocument()
  })

  it('should not require an stt for ofa users', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'admin@acf.hhs.gov',
          roles: [],
          access_request: false,
        },
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
    const { getByText, queryByText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    fireEvent.click(getByText('Request Access'))

    expect(getByText('First Name is required')).toBeInTheDocument()
    expect(getByText('Last Name is required')).toBeInTheDocument()
    expect(queryByText('A state is required')).not.toBeInTheDocument()
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
        <Home />
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
        <Home />
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
    const { getByLabelText } = render(
      <Provider store={store}>
        <Home />
      </Provider>
    )

    const select = getByLabelText('State*', {
      selector: 'input',
    })

    fireEvent.change(select, {
      target: { value: 'alaska' },
    })

    expect(select.value).toEqual('alaska')
  })

  it('routes displays the pending approval message when a user has requested access', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        ...initialState.auth,
        user: {
          account_approval_status: 'Pending',
          access_request: false,
          stt: {
            id: 6,
            type: 'state',
            code: 'CO',
            name: 'Colorado',
          },
        },
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

    render(
      <Provider store={store}>
        <MemoryRouter initialEntries={['/home']}>
          <Routes>
            <Route
              exact
              path="/home"
              element={
                <PrivateRoute title="Home">
                  <Home />
                </PrivateRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </Provider>
    )

    expect(
      screen.getByText(
        `Your request for access is currently being reviewed by an OFA Admin. We'll send you an email when it's been approved.`
      )
    ).toBeInTheDocument()
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
        <Home />
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
      target: { name: 'stt', value: 'Alaska' },
    })

    const form = wrapper.find('.usa-form').hostNodes()
    form.simulate('submit', {
      preventDefault: () => {},
    })

    expect(store.dispatch).toHaveBeenCalled()
  })
})
