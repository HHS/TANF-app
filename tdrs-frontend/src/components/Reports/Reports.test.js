import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
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
      year: '',
      stt: '',
      quarter: '',
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

  const makeTestFile = (name) =>
    new File(['test'], name, {
      type: 'text/plain',
    })

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

    // There are only two STTs in the mock list but the combobox
    // has a default option
    expect(options.length).toEqual(3)
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
    const store = mockStore({
      ...initialState,
      reports: {
        ...initialState.reports,
        year: '2021',
        stt: 'Florida',
        quarter: 'Q3',
      },
    })

    const { getByText, queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()

    fireEvent.click(getByText(/Search/, { selector: 'button' }))

    expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
    expect(getByText('Section 2 - Closed Case Data')).toBeInTheDocument()
    expect(getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
    expect(getByText('Section 4 - Stratum Data')).toBeInTheDocument()
  })

  it('should de-render the UploadReports form after it has been toggled but the year is changed', () => {
    const store = mockStore({
      ...initialState,
      reports: {
        ...initialState.reports,
        year: '2021',
        stt: 'Florida',
        quarter: 'Q3',
      },
    })

    const { getByText, getByLabelText, queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()

    fireEvent.click(getByText(/Search/, { selector: 'button' }))

    expect(queryByText('Section 1 - Active Case Data')).toBeInTheDocument()

    const select = getByLabelText(/Fiscal Year/)

    fireEvent.change(select, {
      target: {
        value: 2021,
      },
    })

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()
  })

  it('should de-render when Cancel is clicked', () => {
    const store = mockStore({
      ...initialState,
      reports: {
        ...initialState.reports,
        year: '2021',
        stt: 'Florida',
        quarter: 'Q3',
      },
    })

    const { getByText, queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/, { selector: 'button' }))

    expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()

    fireEvent.click(getByText(/Cancel/))

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()
  })

  it('should make a request with the selections and upload payloads after clicking Submit Data Files', async () => {
    const store = mockStore({
      ...initialState,
      reports: {
        ...initialState.reports,
        year: '2021',
        stt: 'Florida',
        quarter: 'Q3',
      },
    })
    const origDispatch = store.dispatch
    store.dispatch = jest.fn(origDispatch)

    const { getByText, getByLabelText, getByRole } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/, { selector: 'button' }))

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

  it('should display error labels when user tries to search without making selections', () => {
    const store = mockStore(initialState)

    const { getByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/, { selector: 'button' }))

    expect(getByText('A fiscal year is required')).toBeInTheDocument()
    expect(getByText('A quarter is required')).toBeInTheDocument()
    expect(
      getByText('A state, tribe, or territory is required')
    ).toBeInTheDocument()
  })
})
