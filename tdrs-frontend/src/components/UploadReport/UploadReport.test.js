import React from 'react'
import { thunk } from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { fireEvent, render, waitFor } from '@testing-library/react'
import axios from 'axios'
import Reports from '../Reports/Reports'

import { v4 as uuidv4 } from 'uuid'

import { PREVIEW_HEADING_CLASS } from '../FileUpload/utils'

import UploadReport from './UploadReport'

describe('UploadReport', () => {
  const initialState = {
    auth: { user: { email: 'test@test.com' }, authenticated: true },
    reports: {
      year: '2021',
      stt: 'Florida',
      quarter: 'Q3',
      fileType: 'tanf',
      submittedFiles: [
        {
          fileName: 'test.txt',
          id: 1,
          section: 'Active Case Data',
          uuid: uuidv4(),
          progType: 'tanf',
        },
        {
          fileName: 'testb.txt',
          id: 2,
          section: 'Closed Case Data',
          uuid: uuidv4(),
          progType: 'tanf',
        },
        {
          section: 'Aggregate Data',
          fileType: null,
          fileName: null,
          error: null,
          progType: 'tanf',
        },
        {
          section: 'Stratum Data',
          fileType: null,
          fileName: null,
          error: null,
          progType: 'tanf',
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
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const inputs = container.querySelectorAll('.usa-file-input')

    expect(inputs.length).toEqual(4)
  })

  it('should dispatch the `clearError` and `upload` actions when submit button is clicked', async () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { getByLabelText, getByText, container } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const fileInput = getByLabelText('Section 1 - TANF - Active Case Data')

    const newFile = new File(['HEADER20212A53000TAN1ED\n'], 'test.txt', {
      type: 'text/plain',
    })

    await waitFor(() => {
      fireEvent.change(fileInput, {
        target: {
          files: [newFile],
        },
      })
    })

    await waitFor(() => expect(getByText('test.txt')).toBeInTheDocument())
    expect(store.dispatch).toHaveBeenCalledTimes(3)
    expect(container.querySelectorAll('.has-invalid-file').length).toBe(0)
  })
  it('should prevent upload of file with invalid extension', async () => {
    const store = mockStore(initialState)

    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { getByLabelText, getByText, container } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const fileInput = getByLabelText('Section 1 - TANF - Active Case Data')

    const newFile = new File(['<div>test</div>'], 'test.html', {
      type: 'text/html',
    })

    expect(container.querySelectorAll('.has-invalid-file').length).toBe(0)
    await waitFor(() => {
      fireEvent.change(fileInput, {
        target: {
          files: [newFile],
        },
      })
    })

    //await waitFor(() => expect(getByText('test.html')).toBeInTheDocument()))
    await waitFor(() => {
      expect(store.dispatch).toHaveBeenCalledTimes(3)
      expect(container.querySelectorAll('.has-invalid-file').length).toBe(1)
    })
  })

  it('should render a preview when there is a file available to download', (done) => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { container } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )
    setTimeout(() => {
      const headings = container.querySelectorAll(`.${PREVIEW_HEADING_CLASS}`)
      expect(headings.length).toBeTruthy()

      done()
    }, 100)
  })

  it('should render a div with class "usa-form-group--error" if there is an error', () => {
    // Recreate the store with the initial state, except add an `error`
    // object to one of the files.
    const store = mockStore({
      ...initialState,
      reports: {
        submittedFiles: [
          {
            section: 'Active Case Data',
            fileName: null,
            // This error in the state should create the error state in the UI
            fileType: null,
            error: {
              message: 'something went wrong',
            },
          },
          {
            section: 'Closed Case Data',
            fileName: null,
            fileType: null,
            error: null,
          },
          {
            section: 'Aggregate Data',
            fileName: null,
            fileType: null,
            error: null,
          },
          {
            section: 'Stratum Data',
            fileName: null,
            fileType: null,
            error: null,
          },
        ],
      },
    })

    const { container } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const formGroup = container.querySelector('.usa-form-group')

    expect(formGroup.classList.contains('usa-form-group--error')).toBeTruthy()
  })

  it('should render a div without class "usa-form-group--error" if there is NOT an error', () => {
    const store = mockStore(initialState)
    const { container } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const formGroup = container.querySelector('.usa-form-group')

    expect(formGroup.classList.contains('usa-form-group--error')).toBeFalsy()
  })

  it('should clear input value if there is an error', async () => {
    const store = mockStore(initialState)
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: { id: 1 } })
    )

    const { getByLabelText, getByText } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const fileInput = getByLabelText('Section 1 - TANF - Active Case Data')

    const newFile = new File(['test'], 'test.txt', { type: 'text/plain' })
    const fileList = [newFile]

    await waitFor(() => {
      fireEvent.change(fileInput, {
        target: {
          name: 'Active Case Data',
          files: fileList,
        },
      })
    })

    await waitFor(() => expect(getByText('test.txt')).toBeInTheDocument())
    expect(fileInput.value).toStrictEqual('')
  })
})
