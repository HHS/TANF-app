import React from 'react'
import { fireEvent, render, screen } from '@testing-library/react'

import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'
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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const nameInput = container.querySelector('#firstName')
    expect(nameInput).toBeInTheDocument()
  })

  it('should have a last name input', () => {
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

    const nameInput = container.querySelector('#lastName')

    expect(nameInput).toBeInTheDocument()
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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const submitBtn = container.querySelector('button[type="submit"]')

    expect(submitBtn).toBeInTheDocument()
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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const options = container.querySelectorAll('option')

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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const radio = container.querySelector('#tribe')
    fireEvent.click(radio)

    const options = container.querySelectorAll('option')
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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const radio = container.querySelector('#territory')
    fireEvent.click(radio)

    const options = container.querySelectorAll('option')
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

    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const options = container.querySelectorAll('option')
    expect(options.length).toEqual(0)
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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const form = container.querySelector('.usa-form')

    fireEvent.submit(form, {
      preventDefault: () => {},
    })

    let errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(5)

    const firstNameInput = container.querySelector('#firstName')

    fireEvent.change(firstNameInput, {
      target: {
        value: 's',
        name: 'firstName',
      },
    })

    fireEvent.blur(firstNameInput)

    errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(4)

    const lastNameInput = container.querySelector('#lastName')

    fireEvent.change(lastNameInput, {
      target: {
        value: 's',
        name: 'lastName',
      },
    })

    fireEvent.blur(lastNameInput)

    errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(3)

    const select = container.querySelector('select[name="stt"]')

    // Trigger change with proper name attribute for validation
    fireEvent.change(select, {
      target: {
        value: 'Alaska',
        name: 'stt',
      },
    })

    errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(2)
    expect(errorMessages[0].classList.contains('display-none')).toEqual(false)

    const fraRadioNoButton = container.querySelector('#fra-no')

    fireEvent.click(fraRadioNoButton)

    errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(1)
    expect(errorMessages[0].classList.contains('display-none')).toEqual(true)
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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const form = container.querySelector('.usa-form')

    fireEvent.submit(form, {
      preventDefault: () => {},
    })

    let errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(5)

    const firstNameInput = container.querySelector('#firstName')

    fireEvent.change(firstNameInput, {
      target: {
        name: 'firstName',
        value: 's',
      },
    })

    fireEvent.blur(firstNameInput)

    errorMessages = container.querySelectorAll('.usa-error-message')

    expect(errorMessages.length).toEqual(4)

    fireEvent.change(firstNameInput, {
      target: {
        name: 'firstName',
        value: '',
      },
    })

    fireEvent.blur(firstNameInput)

    errorMessages = container.querySelectorAll('.usa-error-message')

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
    const { container } = render(
      <Provider store={store}>
        <MemoryRouter>
          <Home setInEditMode={jest.fn()} />
        </MemoryRouter>
      </Provider>
    )

    const firstNameInput = container.querySelector('#firstName')
    fireEvent.change(firstNameInput, {
      target: { value: 'harry', name: 'firstName' },
    })

    const lastNameInput = container.querySelector('#lastName')
    fireEvent.change(lastNameInput, {
      target: { name: 'lastName', value: 'potter' },
    })

    const select = container.querySelector('.usa-select')
    fireEvent.change(select, {
      target: { name: 'stt', value: 'Alaska' },
    })

    const fraRadioYesButton = container.querySelector('#fra-yes')
    fireEvent.click(fraRadioYesButton)

    const form = container.querySelector('.usa-form')
    fireEvent.submit(form)

    expect(store.dispatch).toHaveBeenCalled()
  })
})
