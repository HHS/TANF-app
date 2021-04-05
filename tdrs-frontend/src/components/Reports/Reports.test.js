import React from 'react'
import { mount } from 'enzyme'
import { render, fireEvent, waitFor, prettyDOM } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import axios from 'axios'
import Reports from './Reports'
import { SET_FILE, upload } from '../../actions/reports'

describe('Reports', () => {
  const initialState = {
    reports: {
      files: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
      ],
      error: null,
      year: 2020,
    },
    auth: { authenticated: true, user: { email: 'hi@bye.com' } },
  }
  const mockStore = configureStore([thunk])

  const makeTestFile = (name) =>
    new File(['test'], name, {
      type: 'text/plain',
    })

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

  it('should make a request with the selections and upload payloads after clicking Submit Data Files', async () => {
    const store = mockStore(initialState)
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { getByText, getByLabelText, getByRole } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/))

    await waitFor(() => {
      fireEvent.change(getByLabelText('Section 1 - Active Case Data'), {
        target: {
          files: [makeTestFile('section1.txt')],
        },
      })

      fireEvent.change(getByLabelText('Section 2 - Closed Case Data'), {
        target: {
          files: [makeTestFile('section2.txt')],
        },
      })

      fireEvent.change(getByLabelText('Section 3 - Aggregate Data'), {
        target: {
          files: [makeTestFile('section3.txt')],
        },
      })

      fireEvent.change(getByLabelText('Section 4 - Stratum Data'), {
        target: {
          files: [makeTestFile('section4.txt')],
        },
      })
    })
    expect(store.dispatch).toHaveBeenCalledTimes(8)

    // There should be 4 more dispatches upon making the submission,
    // one request to /reports for each file
    fireEvent.click(getByText('Submit Data Files'))
    await waitFor(() => getByRole('alert'))
    expect(store.dispatch).toHaveBeenCalledTimes(12)
  })

  it('should add files to the redux state when uploading', async () => {
    // Because mock-redux-store doesn't actually test reducers,
    // we need to test this separately from the test above
    const store = mockStore(initialState)

    const file1 = makeTestFile('section1.txt')
    const file2 = makeTestFile('section2.txt')
    const file3 = makeTestFile('section3.txt')
    const file4 = makeTestFile('section4.txt')

    await store.dispatch(upload({ file: file1, section: 'Active Case Data' }))
    await store.dispatch(upload({ file: file2, section: 'Closed Case Data' }))
    await store.dispatch(upload({ file: file3, section: 'Aggregate Data' }))
    await store.dispatch(upload({ file: file4, section: 'Stratum Data' }))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({
      fileName: 'section1.txt',
      fileType: 'text/plain',
      section: 'Active Case Data',
      uuid: actions[0].payload.uuid,
    })

    expect(actions[1].type).toBe(SET_FILE)
    expect(actions[1].payload).toStrictEqual({
      fileName: 'section2.txt',
      fileType: 'text/plain',
      section: 'Closed Case Data',
      uuid: actions[1].payload.uuid,
    })

    expect(actions[2].type).toBe(SET_FILE)
    expect(actions[2].payload).toStrictEqual({
      fileName: 'section3.txt',
      fileType: 'text/plain',
      section: 'Aggregate Data',
      uuid: actions[2].payload.uuid,
    })

    expect(actions[3].type).toBe(SET_FILE)
    expect(actions[3].payload).toStrictEqual({
      fileName: 'section4.txt',
      fileType: 'text/plain',
      section: 'Stratum Data',
      uuid: actions[3].payload.uuid,
    })
  })

  it('should add files to the redux state when dispatching uploads', async () => {
    // Because mock-redux-store doesn't actually test reducers,
    // we need to test this separately from the test above
    const store = mockStore(initialState)

    const file1 = makeTestFile('section1.txt')
    const file2 = makeTestFile('section2.txt')
    const file3 = makeTestFile('section3.txt')
    const file4 = makeTestFile('section4.txt')

    await store.dispatch(upload({ file: file1, section: 'Active Case Data' }))
    await store.dispatch(upload({ file: file2, section: 'Closed Case Data' }))
    await store.dispatch(upload({ file: file3, section: 'Aggregate Data' }))
    await store.dispatch(upload({ file: file4, section: 'Stratum Data' }))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({
      fileName: 'section1.txt',
      fileType: 'text/plain',
      section: 'Active Case Data',
      uuid: actions[0].payload.uuid,
    })

    expect(actions[1].type).toBe(SET_FILE)
    expect(actions[1].payload).toStrictEqual({
      fileName: 'section2.txt',
      fileType: 'text/plain',
      section: 'Closed Case Data',
      uuid: actions[1].payload.uuid,
    })

    expect(actions[2].type).toBe(SET_FILE)
    expect(actions[2].payload).toStrictEqual({
      fileName: 'section3.txt',
      fileType: 'text/plain',
      section: 'Aggregate Data',
      uuid: actions[2].payload.uuid,
    })

    expect(actions[3].type).toBe(SET_FILE)
    expect(actions[3].payload).toStrictEqual({
      fileName: 'section4.txt',
      fileType: 'text/plain',
      section: 'Stratum Data',
      uuid: actions[3].payload.uuid,
    })
  })
})
