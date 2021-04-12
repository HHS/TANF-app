import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { fireEvent, render } from '@testing-library/react'

import UploadReport from './UploadReport'

describe('UploadReport', () => {
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
    },
  }
  const mockStore = configureStore([thunk])
  const handleCancel = jest.fn()

  it('should render four inputs for uploading files', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} />
      </Provider>
    )

    const inputs = container.querySelectorAll('.usa-file-input')

    expect(inputs.length).toEqual(4)
  })

  it('should dispatch the `clearError` and `upload` actions when submit button is clicked', () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { getByLabelText } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} />
      </Provider>
    )

    const fileInput = getByLabelText('Section 1 - Active Case Data')

    const newFile = new File(['test'], 'test.txt', { type: 'text/plain' })

    fireEvent.change(fileInput, {
      target: {
        files: [newFile],
      },
    })

    expect(store.dispatch).toHaveBeenCalledTimes(2)
  })

  it('should render a div with class "usa-form-group--error" if there is an error', () => {
    // Recreate the store with the initial state, except add an `error`
    // object to one of the files.
    const store = mockStore({
      ...initialState,
      reports: {
        files: [
          {
            section: 'Active Case Data',
            fileName: null,
            // This error in the state should create the error state in the UI
            error: {
              message: 'something went wrong',
            },
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
      },
    })
    render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} />
      </Provider>
    )

    const formGroup = document.querySelector('.usa-form-group')

    expect(formGroup.classList.contains('usa-form-group--error')).toBeTruthy()
  })

  it('should render a div without class "usa-form-group--error" if there is NOT an error', () => {
    const store = mockStore(initialState)
    render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} />
      </Provider>
    )

    const formGroup = document.querySelector('.usa-form-group')

    expect(formGroup.classList.contains('usa-form-group--error')).toBeFalsy()
  })
})
