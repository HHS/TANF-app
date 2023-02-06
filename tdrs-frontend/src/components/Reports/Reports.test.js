import React from 'react'
import { render, fireEvent, waitFor, getByText } from '@testing-library/react'

import { Provider } from 'react-redux'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import appConfigureStore from '../../configureStore'
import Reports from './Reports'
import { SET_FILE, upload } from '../../actions/reports'

describe('Reports', () => {
  const initialState = {
    reports: {
      files: [
        {
          section: 'Active Case Data',
          file: null,
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          file: null,
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          file: null,
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
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
      fileType: 'tanf',
    },
    stts: {
      sttList: [
        {
          id: 1,
          type: 'state',
          code: 'AL',
          name: 'Alabama',
          ssp: true,
        },
        {
          id: 2,
          type: 'state',
          code: 'AK',
          name: 'Alaska',
          ssp: false,
        },
      ],
      loading: false,
    },
    auth: {
      authenticated: true,
      user: {
        email: 'hi@bye.com',
        stt: {
          id: 2,
          type: 'state',
          code: 'AK',
          name: 'Alaska',
        },
        roles: [{ id: 1, name: 'OFA Admin', permission: [] }],
      },
    },
  }
  const mockStore = configureStore([thunk])

  const makeTestFile = (name) =>
    new File(['test'], name, {
      type: 'text/plain',
    })

  it('should render the Fiscal Year dropdown with however many years and a placeholder', () => {
    const store = mockStore(initialState)
    const { getByLabelText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const today = new Date()
    const fiscalYear =
      today.getMonth() > 8 ? today.getFullYear() + 1 : today.getFullYear()

    // added 1 to include the starting year
    const yearNum = fiscalYear - 2021 + 1

    const select = getByLabelText('Fiscal Year (October - September)')

    expect(select).toBeInTheDocument()

    const options = select.children

    // The placeholder option is included in the length so another 1 was added
    expect(options.length).toEqual(yearNum + 1)
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

    const sttDropdown = getByLabelText(
      'Associated State, Tribe, or Territory*',
      { selector: 'input' }
    )

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

  it('should render the UploadReports form when a year is selected and Search button is clicked', async () => {
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
    await waitFor(() => {
      expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
      expect(getByText('Section 2 - Closed Case Data')).toBeInTheDocument()
      expect(getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
      expect(getByText('Section 4 - Stratum Data')).toBeInTheDocument()
    })
  })

  it('should not de-render the UploadReports form after it has been toggled but the year is changed', async () => {
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

    await waitFor(() => {
      expect(queryByText('Section 1 - Active Case Data')).toBeInTheDocument()
    })

    const select = getByLabelText(/Fiscal Year/)

    fireEvent.change(select, {
      target: {
        value: 2021,
      },
    })

    expect(queryByText('Section 1 - Active Case Data')).toBeInTheDocument()
  })

  it('should de-render when Cancel is clicked', async () => {
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
    await waitFor(() => {
      expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
    })

    fireEvent.click(getByText(/Cancel/))

    expect(queryByText('Section 1 - Active Case Data')).not.toBeInTheDocument()
  })

  it('should make a request with the selections and upload payloads after clicking Submit Data Files', async () => {
    const store = appConfigureStore({
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

    window.HTMLElement.prototype.scrollIntoView = jest.fn(() => null)

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
    expect(store.dispatch).toHaveBeenCalledTimes(14)

    // There should be 4 more dispatches upon making the submission,
    // one request to /reports for each file
    await waitFor(() =>
      expect(getByText('Submit Data Files')).toBeInTheDocument()
    )
    fireEvent.click(getByText('Submit Data Files'))
    await waitFor(() => getByRole('alert'))
    expect(store.dispatch).toHaveBeenCalledTimes(19)
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
      file: file1,
      fileName: 'section1.txt',
      fileType: 'text/plain',
      section: 'Active Case Data',
      uuid: actions[0].payload.uuid,
    })

    expect(actions[1].type).toBe(SET_FILE)
    expect(actions[1].payload).toStrictEqual({
      file: file2,
      fileName: 'section2.txt',
      fileType: 'text/plain',
      section: 'Closed Case Data',
      uuid: actions[1].payload.uuid,
    })

    expect(actions[2].type).toBe(SET_FILE)
    expect(actions[2].payload).toStrictEqual({
      file: file3,
      fileName: 'section3.txt',
      fileType: 'text/plain',
      section: 'Aggregate Data',
      uuid: actions[2].payload.uuid,
    })

    expect(actions[3].type).toBe(SET_FILE)
    expect(actions[3].payload).toStrictEqual({
      file: file4,
      fileName: 'section4.txt',
      fileType: 'text/plain',
      section: 'Stratum Data',
      uuid: actions[3].payload.uuid,
    })
  })

  it('should display error labels when user tries to search without making selections', async () => {
    const store = mockStore(initialState)

    const { getByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    fireEvent.click(getByText(/Search/, { selector: 'button' }))

    await waitFor(() => {
      expect(getByText('A fiscal year is required')).toBeInTheDocument()
      expect(getByText('A quarter is required')).toBeInTheDocument()
      expect(
        getByText('A state, tribe, or territory is required')
      ).toBeInTheDocument()
    })
  })

  describe('search form behaviors', () => {
    const setUpSearchFormBehaviors = async () => {
      // set initial search parameters in initialState
      // using a live redux store here to capture state changes
      // see: https://stackoverflow.com/a/65918951
      const store = appConfigureStore({
        ...initialState,
        auth: {
          authenticated: true,
          user: {
            email: 'hi@bye.com',
            stt: {
              id: 2,
              type: 'state',
              code: 'AK',
              name: 'Alaska',
            },
            roles: [{ id: 1, name: 'Developer', permission: [] }],
          },
        },
        reports: {
          ...initialState.reports,
          year: '2021',
          stt: 'Alaska',
          quarter: 'Q3',
        },
      })

      const { getByText, queryByText, getByLabelText, queryAllByText } = render(
        <Provider store={store}>
          <Reports />
        </Provider>
      )

      await waitFor(() => {
        expect(
          queryByText('Section 1 - Active Case Data')
        ).not.toBeInTheDocument()
        expect(getByText('2021', { selector: 'option' }).selected).toBe(true)
        expect(
          getByText('Quarter 3 (April - June)', { selector: 'option' }).selected
        ).toBe(true)
      })

      return { getByText, queryByText, getByLabelText, queryAllByText }
    }

    it('should only update the report header when search selections are changed after clicking search', async () => {
      const { getByText, getByLabelText, queryByText } =
        await setUpSearchFormBehaviors()

      // search
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() => {
        expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
        expect(
          getByText(
            'Alaska - TANF - Fiscal Year 2021 - Quarter 3 (April - June)'
          )
        ).toBeInTheDocument()
      })

      // make a change to the search selections, but don't click search
      console.log('change year')

      fireEvent.change(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      fireEvent.select(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      fireEvent.change(getByLabelText(/Quarter/), {
        target: { value: 'Q2' },
      })
      fireEvent.select(getByLabelText(/Quarter/), {
        target: { value: 'Q2' },
      })

      // the header should not update
      await waitFor(() =>
        expect(
          queryByText(
            'Alaska -  - Fiscal Year 2022 - Quarter 2 (January - March)'
          )
        ).not.toBeInTheDocument()
      )

      // click search and assert the header updates
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() =>
        expect(
          getByText(
            'Alaska - TANF - Fiscal Year 2022 - Quarter 2 (January - March)'
          )
        ).toBeInTheDocument()
      )
    })

    it('should present a message when searching without first submitting uploaded files', async () => {
      const { getByText, queryByText, getByLabelText } =
        await setUpSearchFormBehaviors()

      // search
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() => {
        expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
        expect(getByText('Section 2 - Closed Case Data')).toBeInTheDocument()
        expect(getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
        expect(getByText('Section 4 - Stratum Data')).toBeInTheDocument()
      })

      // add a file to be uploaded, but don't submit
      fireEvent.change(getByLabelText('Section 1 - Active Case Data'), {
        target: {
          files: [makeTestFile('section1.txt')],
        },
      })

      await waitFor(() => expect(getByText('section1.txt')).toBeInTheDocument())

      // make a change to the search selections and click search
      fireEvent.change(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      fireEvent.select(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      await waitFor(() =>
        expect(getByText('2022', { selector: 'option' }).selected).toBe(true)
      )

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      // the modal should display
      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )
    })

    it('should allow the user to cancel the error modal and retain previous search selections', async () => {
      const { getByText, queryByText, getByLabelText } =
        await setUpSearchFormBehaviors()

      // search
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() => {
        expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
        expect(getByText('Section 2 - Closed Case Data')).toBeInTheDocument()
        expect(getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
        expect(getByText('Section 4 - Stratum Data')).toBeInTheDocument()
      })

      // add a file to be uploaded, but don't submit
      fireEvent.change(getByLabelText('Section 1 - Active Case Data'), {
        target: {
          files: [makeTestFile('section1.txt')],
        },
      })

      await waitFor(() => expect(getByText('section1.txt')).toBeInTheDocument())

      // make a change to the search selections and click search
      fireEvent.change(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      fireEvent.select(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      await waitFor(() =>
        expect(getByText('2022', { selector: 'option' }).selected).toBe(true)
      )

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      // the modal should display
      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      // click cancel
      fireEvent.click(getByText(/Cancel/, { selector: '#modal button' }))

      // assert file still exists, search params are the same as initial
      await waitFor(() => {
        expect(getByText('section1.txt')).toBeInTheDocument()
        expect(getByText('2021', { selector: 'option' }).selected).toBe(true)
      })
    })

    it('should allow the user to discard un-submitted files and continue with the new search', async () => {
      const { getByText, queryByText, getByLabelText } =
        await setUpSearchFormBehaviors()

      // search
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() => {
        expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
        expect(getByText('Section 2 - Closed Case Data')).toBeInTheDocument()
        expect(getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
        expect(getByText('Section 4 - Stratum Data')).toBeInTheDocument()
      })

      // add a file to be uploaded, but don't submit
      fireEvent.change(getByLabelText('Section 1 - Active Case Data'), {
        target: {
          files: [makeTestFile('section1.txt')],
        },
      })

      await waitFor(() => expect(getByText('section1.txt')).toBeInTheDocument())

      // make a change to the search selections and click search
      fireEvent.change(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      fireEvent.select(getByLabelText(/Fiscal Year/), {
        target: { value: '2022' },
      })
      await waitFor(() =>
        expect(getByText('2022', { selector: 'option' }).selected).toBe(true)
      )

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      // the modal should display
      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      // click cancel
      fireEvent.click(
        getByText(/Discard and Search/, { selector: '#modal button' })
      )

      // assert file is cleared, search params are updated
      await waitFor(() => {
        expect(queryByText('section1.txt')).not.toBeInTheDocument()
        expect(getByText('2022', { selector: 'option' }).selected).toBe(true)
      })
    })

    it('Shows submission history when the Submission History tab is clicked', async () => {
      const { getByText, queryAllByText, queryByText } =
        await setUpSearchFormBehaviors()

      // search
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() => {
        expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
        expect(
          getByText(
            'Alaska - TANF - Fiscal Year 2021 - Quarter 3 (April - June)'
          )
        ).toBeInTheDocument()

        expect(getByText('Current Submission')).toBeInTheDocument()
        expect(getByText('Submission History')).toBeInTheDocument()
        expect(queryByText('No data available.')).not.toBeInTheDocument()
      })

      fireEvent.click(getByText('Submission History'))

      await waitFor(() => {
        expect(getByText('Section 1 - Active Case Data')).toBeInTheDocument()
        expect(queryAllByText('No data available.')).toHaveLength(4)
      })
    })
  })

  it('should show next calander year in fiscal year dropdown in October', () => {
    const currentYear = new Date().getFullYear()

    const getNow = () => new Date(Date.now())

    jest
      .spyOn(global.Date, 'now')
      .mockImplementation(() =>
        new Date(`October 01, ${currentYear}`).valueOf()
      )
    const now = getNow()
    expect(now).toEqual(new Date(`October 01, ${currentYear}`))
    const store = mockStore(initialState)

    const { getByLabelText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = getByLabelText('Fiscal Year (October - September)')
    const options = select.children
    const expected = options.item(1).value

    expect(expected).toEqual((currentYear + 1).toString())
  })

  it('should show current calander year in fiscal year dropdown in January', () => {
    const currentYear = new Date().getFullYear()

    const getNow = () => new Date(Date.now())

    jest
      .spyOn(global.Date, 'now')
      .mockImplementation(() =>
        new Date(`January 01, ${currentYear}`).valueOf()
      )
    const now = getNow()
    expect(now).toEqual(new Date(`January 01, ${currentYear}`))
    const store = mockStore(initialState)

    const { getByLabelText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    const select = getByLabelText('Fiscal Year (October - September)')
    const options = select.children
    const expected = options.item(1).value

    expect(expected).toEqual(currentYear.toString())
  })

  it('Non OFA Admin should show the data files section when the user has an stt with ssp set to true', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        ...initialState.auth,
        user: {
          ...initialState.auth.user,
          roles: [],
          stt: {
            name: 'Alabama',
          },
        },
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    expect(getByText('File Type')).toBeInTheDocument()
  })

  // should not render the File Type section if the user is not an OFA Admin and the stt has ssp set to false
  it('Non OFA Admin should not show the data files section when the user has an stt with ssp set to false', () => {
    const store = mockStore({
      ...initialState,
      auth: {
        ...initialState.auth,
        user: {
          ...initialState.auth.user,
          roles: [],
          stt: {
            name: 'Alaska',
          },
        },
      },
    })

    const { queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    expect(queryByText('File Type')).not.toBeInTheDocument()
  })

  it('OFA Admin should see the data files section when they select a stt with ssp set to true', () => {
    const store = mockStore({
      ...initialState,
      reports: {
        ...initialState.reports,
        stt: 'Alabama',
      },
    })

    const { getByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    expect(getByText('File Type')).toBeInTheDocument()
  })

  it('OFA Admin should not see the data files section when they select a stt with ssp set to false', () => {
    const store = mockStore({
      ...initialState,
      reports: {
        ...initialState.reports,
        stt: 'Alaska',
      },
    })

    const { queryByText } = render(
      <Provider store={store}>
        <Reports />
      </Provider>
    )

    expect(queryByText('File Type')).not.toBeInTheDocument()
  })
})
