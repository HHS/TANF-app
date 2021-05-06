import React from 'react'
import thunk from 'redux-thunk'
import { Provider } from 'react-redux'
import configureStore from 'redux-mock-store'
import { fireEvent, render } from '@testing-library/react'
import axios from 'axios'

import { v4 as uuidv4 } from 'uuid'

import UploadReport from './UploadReport'

describe('UploadReport', () => {
  const initialState = {
    auth: { user: { email: 'test@test.com' }, authenticated: true },
    reports: {
      files: [
        {
          fileName: 'test.txt',
          section: 'Active Case Data',
          uuid: uuidv4(),
        },
        {
          fileName: 'testb.txt',
          section: 'Closed Case Data',
          uuid: uuidv4(),
        },
        {
          section: 'Aggregate Data',
          fileType: null,
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          fileType: null,
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
        <UploadReport handleCancel={handleCancel} header="Some header" />
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
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const fileInput = getByLabelText('Section 1 - Active Case Data')

    const newFile = new File(['test'], 'test.txt', { type: 'text/plain' })

    fireEvent.change(fileInput, {
      target: {
        files: [newFile],
      },
    })

    expect(store.dispatch).toHaveBeenCalledTimes(3)
  })
  it('should display a download button when the file is available for download.', () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { container, getByLabelText } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} />
      </Provider>
    )

    const buttons = container.querySelectorAll('.tanf-file-download-btn')
    expect(buttons.length).toBe(2)

    //expect(store.dispatch).toHaveBeenCalledTimes(2)
  })

  it('should render a preview when there is a file available to download',(done) => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { container, getByLabelText } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} />
      </Provider>
    )

    setTimeout(() => {
      const PREFIX = 'usa'

      const PREVIEW_HEADING_CLASS = `${PREFIX}-file-input__preview-heading`

      const PREVIEW_CLASS = `${PREFIX}-file-input__preview`
      const GENERIC_PREVIEW_CLASS_NAME = `${PREFIX}-file-input__preview-image`
      const ACCEPTED_FILE_MESSAGE_CLASS = `${PREFIX}-file-input__accepted-files-message`
      const TARGET_CLASS = `${PREFIX}-file-input__target`

      const GENERIC_PREVIEW_CLASS = `${GENERIC_PREVIEW_CLASS_NAME}--generic`

      const LOADING_CLASS = 'is-loading'
      const INVALID_FILE_CLASS = 'has-invalid-file'
      const HIDDEN_CLASS = 'display-none'
      const INSTRUCTIONS_CLASS = `${PREFIX}-file-input__instructions`
      const headings = container.querySelectorAll(`.${PREVIEW_HEADING_CLASS}`)
      expect(headings.length).toBe(2)
      done()
    },500)

  })

  it('should render a div with class "usa-form-group--error" if there is an error', () => {
    // Recreate the store with the intial state, except add an `error`
    // object to one of the files.
    const store = mockStore({
      ...initialState,
      reports: {
        files: [
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

  it('should clear input value if there is an error', () => {
    const store = mockStore(initialState)
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({ data: { id: 1 } })
    )

    const { getByLabelText } = render(
      <Provider store={store}>
        <UploadReport handleCancel={handleCancel} header="Some header" />
      </Provider>
    )

    const fileInput = getByLabelText('Section 1 - Active Case Data')

    const newFile = new File(['test'], 'test.txt', { type: 'text/plain' })
    const fileList = [newFile]

    fireEvent.change(fileInput, {
      target: {
        name: 'Active Case Data',
        files: fileList,
      },
    })

    expect(fileInput.value).toStrictEqual('')
  })
})
