import React from 'react'
import { fireEvent, render } from '@testing-library/react'

import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'
import { mount } from 'enzyme'
import Home from '.'
import configureStore from 'redux-mock-store'
import * as authSelectors from '../../selectors/auth'
import { MemoryRouter } from 'react-router-dom'

// Mock the auth selectors
jest.mock('../../selectors/auth', () => ({
  ...jest.requireActual('../../selectors/auth'),
  accountIsInReview: jest.fn(() => false),
  accountStatusIsApproved: jest.fn(() => false),
  accountIsRegionalStaff: jest.fn(() => false),
}))

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

describe('Pre-approval Home page', () => {
  const mockStore = configureStore([thunk])

  it('should have a first name input', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const nameInput = wrapper.find('#firstName')
    expect(nameInput).toExist()
  })

  it('should have a last name input', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const nameInput = wrapper.find('#lastName')

    expect(nameInput).toExist()
  })

  it('should set firstName state value to equal the input value', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const input = container.querySelector('input[name="firstName"]')

    fireEvent.change(input, {
      target: { value: 'Peter' },
    })

    expect(input.value).toEqual('Peter')
  })

  it('should set lastName state value to equal the input value', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const input = container.querySelector('input[name="lastName"]')

    fireEvent.change(input, {
      target: { value: 'Parker' },
    })

    expect(input.value).toEqual('Parker')
  })

  it('should have a submit button', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

    const store = mockStore(initialState)
    const wrapper = mount(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const submitBtn = wrapper.find('button[type="submit"]')

    expect(submitBtn).toExist()
  })

  it('should mount a list of stt options based on stts from the store', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const options = wrapper.find('option')

    expect(options.length).toEqual(3)
  })

  it('should mount a list of tribe options based on stts from the store', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
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
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
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
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const options = wrapper.find('option')
    expect(options).toEqual({})
  })

  it('should have errors when you try to submit and first name does not have at least 1 character', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    fireEvent.click(getByText('Request Access'))

    expect(getByText('First Name is required')).toBeInTheDocument()
    expect(getByText('Last Name is required')).toBeInTheDocument()
    expect(getByText('A state is required')).toBeInTheDocument()
  })

  it('should not require an stt for ofa users', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    fireEvent.click(getByText('Request Access'))

    expect(getByText('First Name is required')).toBeInTheDocument()
    expect(getByText('Last Name is required')).toBeInTheDocument()
    expect(queryByText('A state is required')).not.toBeInTheDocument()
  })

  it('should display regional vs central radio control', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
    const { getByText } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    expect(
      getByText('Do you work for an OFA Regional Office?*')
    ).toBeInTheDocument()
    expect(getByText('No')).toBeInTheDocument()
    expect(getByText('Yes')).toBeInTheDocument()
  })

  it('should toggle region checkboxes', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(true)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    expect(
      getByText('Do you work for an OFA Regional Office?*')
    ).toBeInTheDocument()

    fireEvent.click(getByText('Yes'))

    expect(getByText('Select Your Regional Office(s)*')).toBeInTheDocument()
    expect(getByText('Region 6 (Dallas)')).toBeInTheDocument()

    fireEvent.click(getByText('No'))

    expect(
      queryByText('Select Your Regional Office(s):*')
    ).not.toBeInTheDocument()
    expect(queryByText('Region 6 (Dallas)')).not.toBeInTheDocument()
  })

  it('should have 3 errors when regions toggled and no selections made', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
    const { getByText } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    expect(
      getByText('Do you work for an OFA Regional Office?*')
    ).toBeInTheDocument()

    fireEvent.click(getByText('Yes'))

    expect(getByText('Select Your Regional Office(s)*')).toBeInTheDocument()
    expect(getByText('Region 6 (Dallas)')).toBeInTheDocument()

    fireEvent.click(getByText('Request Access'))
    expect(getByText('There are 3 errors in this form')).toBeInTheDocument()
  })

  it('should have 2 errors after region selection when already invalid', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
    const { getByText } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    expect(
      getByText('Do you work for an OFA Regional Office?*')
    ).toBeInTheDocument()

    fireEvent.click(getByText('Yes'))

    expect(getByText('Select Your Regional Office(s)*')).toBeInTheDocument()
    expect(getByText('Region 6 (Dallas)')).toBeInTheDocument()

    fireEvent.click(getByText('Request Access'))
    expect(getByText('There are 3 errors in this form')).toBeInTheDocument()

    fireEvent.click(getByText('Region 6 (Dallas)'))
    expect(getByText('There are 2 errors in this form')).toBeInTheDocument()
  })

  it('should have 2 errors after region checkboxes are hidden', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
    const { getByText } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    expect(
      getByText('Do you work for an OFA Regional Office?*')
    ).toBeInTheDocument()

    fireEvent.click(getByText('Yes'))

    expect(getByText('Select Your Regional Office(s)*')).toBeInTheDocument()
    expect(getByText('Region 6 (Dallas)')).toBeInTheDocument()

    fireEvent.click(getByText('Request Access'))
    expect(getByText('There are 3 errors in this form')).toBeInTheDocument()

    fireEvent.click(getByText('No'))
    expect(getByText('There are 2 errors in this form')).toBeInTheDocument()
  })

  it('should be able to select and deselect multiple regions', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
    const { getByText } = render(
      <Provider store={store}>
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    expect(
      getByText('Do you work for an OFA Regional Office?*')
    ).toBeInTheDocument()

    fireEvent.click(getByText('Yes'))

    expect(getByText('Select Your Regional Office(s)*')).toBeInTheDocument()
    expect(getByText('Region 6 (Dallas)')).toBeInTheDocument()

    fireEvent.click(getByText('Region 6 (Dallas)'))
    fireEvent.click(getByText('Region 8 (Denver)'))
    fireEvent.click(getByText('Region 6 (Dallas)'))
  })

  it('should remove error message as inputs are filled', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const form = wrapper.find('.usa-form').hostNodes()

    form.simulate('submit', {
      preventDefault: () => {},
    })

    let errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(5)

    const firstNameInput = wrapper.find('#firstName')

    firstNameInput.simulate('change', {
      target: {
        value: 's',
        name: 'firstName',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(4)

    const lastNameInput = wrapper.find('#lastName')

    lastNameInput.simulate('change', {
      target: {
        value: 's',
        name: 'lastName',
      },
    })

    lastNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(3)

    const select = wrapper.find('.usa-select')

    select.simulate('change', {
      target: {
        value: 'alaska',
        name: 'stt',
      },
    })

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(2)
    expect(errorMessages.first().hasClass('display-none')).toEqual(false)

    const fraRadioNoButton = wrapper.find('#fra-no')

    fraRadioNoButton.simulate('change', {
      target: {
        value: 'false',
        name: 'hasFRAAccess',
      },
    })

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(1)
    expect(errorMessages.first().hasClass('display-none')).toEqual(true)
  })

  it('should display an error message when the input has been touched', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
      </Provider>
    )

    const form = wrapper.find('.usa-form').hostNodes()

    form.simulate('submit', {
      preventDefault: () => {},
    })

    let errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(5)

    const firstNameInput = wrapper.find('#firstName')

    firstNameInput.simulate('change', {
      target: {
        name: 'firstName',
        value: 's',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(4)

    firstNameInput.simulate('change', {
      target: {
        name: 'firstName',
        value: '',
      },
    })

    firstNameInput.simulate('blur')

    errorMessages = wrapper.find('.usa-error-message')

    expect(errorMessages.length).toEqual(5)
  })

  it('should set the Select element value to the value of the event when there is a selected stt', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
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

  it('should dispatch "requestAccess" when form is submitted', () => {
    authSelectors.accountIsInReview.mockReturnValue(false)
    authSelectors.accountStatusIsApproved.mockReturnValue(false)
    authSelectors.accountIsRegionalStaff.mockReturnValue(false)

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
        <MemoryRouter>
            <Home setInEditMode={jest.fn()} />
          </MemoryRouter>
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

    const fraRadioYesButton = wrapper.find('#fra-yes')
    fraRadioYesButton.simulate('change', {
      target: { name: 'hasFRAAccess', value: 'true' },
    })

    const form = wrapper.find('.usa-form').hostNodes()
    form.simulate('submit', {
      preventDefault: () => {},
    })

    expect(store.dispatch).toHaveBeenCalled()
  })
})
