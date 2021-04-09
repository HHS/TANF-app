import React from 'react'
import { mount } from 'enzyme'
import { render, fireEvent } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import Reports from './Reports'
import Button from '../Button'

describe('Reports', () => {
  const initialState = {
    reports: {
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
          error: null,
        },
      ],
      error: null,
      year: '',
      stt: '',
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
      ],
      loading: false,
    },
    auth: {
      authenticated: true,
      user: {
        email: 'hi@bye.com',
        roles: [{ id: 1, name: 'OFA Admin', permission: [] }],
      },
    },
  }
  const mockStore = configureStore([thunk])

  it('should render the Fiscal Year dropdown with two options and a placeholder', () => {
    const store = mockStore(initialState)
    const { getByLabelText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = getByLabelText('Fiscal Year (October - September)')

    expect(select).toBeInTheDocument()

    const options = select.children

    // The placeholder option is included in the length
    expect(options.length).toEqual(3)
  })

  it('should render the STT dropdown with one option, when the user is an OFA Admin', () => {
    const store = mockStore(initialState)
    const { getByTestId } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = getByTestId('stt-combobox')

    const options = select.children

    expect(options.length).toEqual(2)
  })

  it('should not render the STT if the user is not an OFA Admin', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          roles: [], // Remove the OFA Admin role
        },
      },
    })

    const { queryByTestId } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = queryByTestId('stt-combobox')

    expect(select).toBe(null)
  })

  it('should select an STT and a year on the Reports page', () => {
    const store = mockStore(initialState)
    const { getByText, getByLabelText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const sttDropdown = getByLabelText('Associated State, Tribe, or Territory')

    // Due to weirdness with USWDS, fire a change event instead of a select
    fireEvent.change(sttDropdown, {
      target: { value: 'alaska' },
    })

    expect(sttDropdown.value).toEqual('alaska')

    const yearsDropdown = getByLabelText('Fiscal Year (October - September)')

    fireEvent.select(yearsDropdown, {
      target: { value: '2021' },
    })

    expect(getByText('2021', { selector: 'option' }).selected).toBe(true)
  })

  it('should render the UploadReports form when a year is selected and Search button is clicked', () => {
    const store = mockStore(initialState)

    const { getByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/))

    expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
    expect(getByText('Section 2 - Closed Case Data')).toBeInTheDocument()
    expect(getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
    expect(getByText('Section 4 - Stratum Data')).toBeInTheDocument()
  })

  it('should de-render the UploadReports form after it has been toggled but the year is changed', () => {
    const store = mockStore(initialState)

    const { getByText, getByLabelText, queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/))

    const select = getByLabelText('Fiscal Year (October - September)')

    fireEvent.change(select, {
      target: {
        value: 2021,
      },
    })

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()
  })

  it('should de-render when Cancel is clicked', () => {
    const store = mockStore(initialState)

    const { getByText, queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/))

    expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()

    fireEvent.click(getByText(/Cancel/))

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()
  })
})
