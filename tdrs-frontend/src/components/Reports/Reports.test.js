import React from 'react'
import { mount } from 'enzyme'
import { render, fireEvent } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import Reports from './Reports'

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
      year: 2020,
    },
    auth: { authenticated: true, user: { email: 'hi@bye.com' } },
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

  it('should dispatch setYear when a year is selected', () => {
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
