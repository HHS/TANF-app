import React from 'react'
import { mount } from 'enzyme'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { render, fireEvent, prettyDOM } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Reports from './Reports'
import Button from '../Button'

describe('Reports', () => {
  const initialState = {
    reports: {
      file: null,
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

    const select = getByLabelText('Fiscal Year')

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

    expect(options.length).toEqual(1)
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
    const { getByTestId, getByText, getByLabelText } = render(
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

    const yearsDropdown = getByLabelText('Fiscal Year')

    fireEvent.select(yearsDropdown, {
      target: { value: '2021' },
    })

    expect(getByText('2021', { selector: 'option' }).selected).toBe(true)
  })

  it('should change route to `/reports/:year/upload` on click of `Begin Report` button', () => {
    const store = mockStore({
      ...initialState,
      reports: {
        file: null,
        error: null,
        year: '2020',
        stt: '',
      },
    })
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
})
