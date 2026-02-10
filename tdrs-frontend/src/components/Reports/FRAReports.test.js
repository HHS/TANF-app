import React from 'react'
import { fireEvent, waitFor, render, within } from '@testing-library/react'
import axios from 'axios'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router-dom'
import { FRAReports } from '.'
import configureStore from '../../configureStore'

const initialState = {
  auth: {
    authenticated: false,
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
}

const mockStore = (initial = {}) => configureStore(initial)

const makeTestFile = (name, contents = ['test'], type = 'text/plain') =>
  new File(contents, name, { type })

describe('FRA Reports Page', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })
  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
  })

  it('Renders', () => {
    const store = mockStore()
    const { getByText, queryByText } = render(
      <Provider store={store}>
        <MemoryRouter>
          <FRAReports />
        </MemoryRouter>
      </Provider>
    )

    // search form elements exist
    expect(getByText('File Type*')).toBeInTheDocument()
    expect(getByText('Fiscal Year (October - September)*')).toBeInTheDocument()
    expect(getByText('Fiscal Quarter*')).toBeInTheDocument()
    expect(getByText('FRA Data Reporting Guidelines')).toBeInTheDocument()
    expect(getByText('Work Outcomes of TANF Exiters')).toBeInTheDocument()

    // error and upload for elements do not
    expect(queryByText('Submit Report')).not.toBeInTheDocument()
  })

  describe('Search form', () => {
    it('Shows STT combobox if admin role', () => {
      const state = {
        ...initialState,
        auth: {
          authenticated: true,
          user: {
            email: 'hi@bye.com',
            stt: null,
            roles: [{ id: 1, name: 'OFA System Admin', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)

      const { getByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      expect(getByText('State, Tribe, or Territory*')).toBeInTheDocument()
    })

    it('Does not show STT combobox if not admin', () => {
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)

      const { queryByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      expect(
        queryByText('Associated State, Tribe, or Territory*')
      ).not.toBeInTheDocument()
    })

    it('Shows missing STT error if STT not set', () => {
      const state = {
        ...initialState,
        auth: {
          authenticated: true,
          user: {
            email: 'hi@bye.com',
            stt: null,
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)

      const { getByText, queryByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      expect(
        queryByText('Associated State, Tribe, or Territory*')
      ).not.toBeInTheDocument()
      expect(getByText('An STT is not set for this user.')).toBeInTheDocument()
    })

    it('Shows upload form once search has been clicked', async () => {
      jest.mock('axios')
      const mockAxios = axios

      let searchUrl = null
      mockAxios.get.mockImplementation((url) => {
        if (url.includes('/data_files/')) {
          searchUrl = url
        }
        return Promise.resolve({ data: [] })
      })

      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)

      const { getByText, queryByText, getByLabelText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      // fill out the form values - this will trigger the API call
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2021' } })

      const quarterDropdown = getByLabelText('Fiscal Quarter*')
      fireEvent.change(quarterDropdown, { target: { value: 'Q1' } })

      // Wait for the API call to complete and upload form to be displayed
      await waitFor(() => {
        expect(
          getByText(
            'Alaska - Work Outcomes of TANF Exiters - Fiscal Year 2021 - Quarter 1 (October - December)'
          )
        ).toBeInTheDocument()
        expect(getByText('Submit Report')).toBeInTheDocument()
      })

      expect(
        searchUrl.includes('&file_type=Work Outcomes of TANF Exiters')
      ).toBe(true)

      // fields don't have errors
      expect(
        queryByText('A state, tribe, or territory is required')
      ).not.toBeInTheDocument()
      expect(queryByText('A fiscal year is required')).not.toBeInTheDocument()
      expect(queryByText('A quarter is required')).not.toBeInTheDocument()
      expect(
        queryByText('There are 3 error(s) in this form')
      ).not.toBeInTheDocument()
    })
  })

  describe('Upload form', () => {
    const setup = async () => {
      jest.mock('axios')
      const mockAxios = axios

      window.HTMLElement.prototype.scrollIntoView = () => {}
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)
      const origDispatch = store.dispatch
      store.dispatch = jest.fn(origDispatch)

      mockAxios.post.mockResolvedValue({
        data: { id: 1 },
      })

      const component = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      const { getByLabelText, getByText } = component

      // fill out the form values before clicking search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2021' } })

      const quarterDropdown = getByLabelText('Fiscal Quarter*')
      fireEvent.change(quarterDropdown, { target: { value: 'Q1' } })

      await waitFor(() => {
        expect(
          getByText(
            'Alaska - Work Outcomes of TANF Exiters - Fiscal Year 2021 - Quarter 1 (October - December)'
          )
        ).toBeInTheDocument()
        expect(
          getByText(
            'The Work Outcomes of TANF Exiters report contains the Social Security Numbers (SSNs) of all work-eligible individuals who exit TANF in a given quarter and the dates in YYYYMM format that each individual exited TANF.'
          )
        ).toBeInTheDocument()
        expect(getByText('Submit Report')).toBeInTheDocument()
      })

      return { ...component, ...store, mockAxios }
    }

    it('Allows csv files to be selected and submitted', async () => {
      const { getByText, dispatch, container } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      const submitButton = getByText('Submit Report')
      fireEvent.click(submitButton)

      await waitFor(() =>
        expect(
          getByText(
            `Successfully submitted section: Work Outcomes of TANF Exiters on ${new Date().toDateString()}`
          )
        ).toBeInTheDocument()
      )
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(6))
    })

    it('Allows xlsx files to be selected and submitted', async () => {
      const { getByText, dispatch, container } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: {
          files: [
            makeTestFile('report.xlsx', ['asdfad'], 'application/vnd.ms-excel'),
          ],
        },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.xlsx. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      const submitButton = getByText('Submit Report')
      fireEvent.click(submitButton)

      await waitFor(() =>
        expect(
          getByText(
            `Successfully submitted section: Work Outcomes of TANF Exiters on ${new Date().toDateString()}`
          )
        ).toBeInTheDocument()
      )
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(6))
    })

    it('Shows a spinner until submission history updates', async () => {
      // jest.spyOn(global, 'setTimeout')
      const {
        getByText,
        queryAllByTestId,
        queryAllByText,
        dispatch,
        mockAxios,
        container,
      } = await setup()

      mockAxios.post.mockResolvedValue({
        data: {
          id: 1,
          original_filename: 'testFile.txt',
          extension: 'txt',
          quarter: 'Q1',
          section: 'Work Outcomes of TANF Exiters',
          slug: '1234-5-6-7890',
          year: '2021',
          s3_version_id: '3210',
          created_at: '2025-02-07T23:38:58+0000',
          submitted_by: 'Test Testerson',
          has_error: false,
          summary: null,
          latest_reparse_file_meta: '',
        },
      })

      let times = 0
      mockAxios.get.mockImplementation((url) => {
        if (url.includes('/data_files/1/')) {
          // status
          times += 1
          return Promise.resolve({
            data: {
              id: 1,
              summary: { status: times > 1 ? 'Approved' : 'Pending' },
            },
          })
        } else {
          // submission history
          return Promise.resolve({
            data: [
              {
                id: 1,
                original_filename: 'testFile.txt',
                extension: 'txt',
                quarter: 'Q1',
                section: 'Work Outcomes of TANF Exiters',
                slug: '1234-5-6-7890',
                year: '2021',
                s3_version_id: '3210',
                created_at: '2025-02-07T23:38:58+0000',
                submitted_by: 'Test Testerson',
                has_error: false,
                summary: { status: 'Pending' },
                latest_reparse_file_meta: '',
              },
            ],
          })
        }
      })

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: {
          files: [
            makeTestFile('report.xlsx', ['asdfad'], 'application/vnd.ms-excel'),
          ],
        },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.xlsx. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      const submitButton = getByText('Submit Report')
      fireEvent.click(submitButton)

      await waitFor(() =>
        expect(
          getByText(
            `Successfully submitted section: Work Outcomes of TANF Exiters on ${new Date().toDateString()}`
          )
        ).toBeInTheDocument()
      )
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(6))

      expect(queryAllByTestId('spinner')).toHaveLength(3)
      expect(queryAllByText('Pending')).toHaveLength(2)

      jest.runOnlyPendingTimers()

      expect(mockAxios.get).toHaveBeenCalledTimes(4)
      expect(times).toBe(2)

      await waitFor(() => {
        expect(getByText('Approved')).toBeInTheDocument()
      })

      expect(queryAllByTestId('spinner')).toHaveLength(0)
      expect(queryAllByText('Pending')).toHaveLength(0)
      expect(getByText('Approved')).toBeInTheDocument()
    })

    it('Shows an error if file submission failed', async () => {
      jest.mock('axios')
      const mockAxios = axios
      const { getByText, dispatch, container } = await setup()

      mockAxios.post.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      const submitButton = getByText('Submit Report')
      fireEvent.click(submitButton)

      await waitFor(() =>
        expect(getByText('Error: Mock fail response')).toBeInTheDocument()
      )
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(4))
    })

    it('Shows an error if a no file is selected for submission', async () => {
      const { getByText } = await setup()

      const submitButton = getByText('Submit Report', { selector: 'button' })
      fireEvent.click(submitButton)

      await waitFor(() =>
        expect(
          getByText('No changes have been made to data files')
        ).toBeInTheDocument()
      )
    })

    it('Shows an error if a non-allowed file type is selected', async () => {
      const { getByText, dispatch, getByRole, container } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.png', ['png'], 'img/png')] },
      })
      await waitFor(() => {
        expect(
          getByText(
            'Invalid extension. Accepted file types are: .csv or .xlsx.'
          )
        ).toBeInTheDocument()
      })

      const submitButton = getByText('Submit Report', { selector: 'button' })
      fireEvent.click(submitButton)

      await waitFor(() => getByRole('alert'))
      expect(dispatch).toHaveBeenCalledTimes(3)
    })

    it('Shows a message if input is changed with an non-uploaded file', async () => {
      const { getByText, container, getByLabelText, queryByText } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })

      await waitFor(() => {
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      })

      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      fireEvent.click(getByText(/OK/, { selector: '#modal button' }))

      const quarterDropdown = getByLabelText('Fiscal Quarter*')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })

      await waitFor(() => {
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })
    })

    it('Cancels the upload if Cancel is clicked', async () => {
      const { getByText, container, queryByText } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })

      await waitFor(() => {
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      })

      fireEvent.click(getByText(/Cancel/, { selector: 'button' }))

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      fireEvent.click(getByText(/OK/, { selector: '#modal button' }))

      await waitFor(() => {
        expect(
          queryByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).not.toBeInTheDocument()
        expect(queryByText(/Submit Report/)).not.toBeInTheDocument()
      })
    })

    it('Does not show a message if input is changed after uploading a file', async () => {
      const {
        getByText,
        getByRole,
        container,
        getByLabelText,
        queryByText,
        dispatch,
      } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      fireEvent.click(getByText(/Submit Report/, { selector: 'button' }))
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(4))

      await waitFor(() => getByRole('alert'))

      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      const quarterDropdown = getByLabelText('Fiscal Quarter*')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })

      await waitFor(() => {
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).not.toBeInTheDocument()
      )
    })

    it('Allows the user to cancel the error modal and retain previous search selections', async () => {
      const { getByText, queryByText, getByLabelText, container, dispatch } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      // make a change to the search selections and click search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      // click cancel
      fireEvent.click(getByText(/Cancel/, { selector: '#modal button' }))

      // assert file still exists, search params are the same as initial, dispatch not called
      await waitFor(() => {
        expect(dispatch).toHaveBeenCalledTimes(3)
        expect(queryByText('Files Not Submitted')).not.toBeInTheDocument()
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
        expect(getByText('2021', { selector: 'option' }).selected).toBe(true)
        expect(
          getByText('Quarter 1 (October - December)', { selector: 'option' })
            .selected
        ).toBe(true)
      })
    })

    it('Allows the user to discard the error modal and continue with a new search', async () => {
      const { getByText, queryByText, getByLabelText, container } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.csv')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      // make a change to the search selections
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      // click discard
      const button = getByText(/OK/, {
        selector: '#modal button',
      })
      fireEvent.click(button)

      const quarterDropdown = getByLabelText('Fiscal Quarter*')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })

      await waitFor(() => {
        expect(getByText('2024', { selector: 'option' }).selected).toBe(true)
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })

      // assert file discarded, search params updated
      await waitFor(() => {
        // expect(dispatch).toHaveBeenCalledTimes(2)
        expect(queryByText('Files Not Submitted')).not.toBeInTheDocument()
        expect(
          queryByText(
            'Selected File report.csv. To change the selected file, click this button.'
          )
        ).not.toBeInTheDocument()
        expect(getByText('2024', { selector: 'option' }).selected).toBe(true)
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
        expect(
          getByText(
            'Alaska - Work Outcomes of TANF Exiters - Fiscal Year 2024 - Quarter 2 (January - March)'
          )
        ).toBeInTheDocument()
      })
    })
  })

  describe('Submission History', () => {
    const setup = async (submissionHistoryApiResponse = []) => {
      jest.mock('axios')
      const mockAxios = axios

      window.HTMLElement.prototype.scrollIntoView = () => {}
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
        fraReports: {
          isLoadingSubmissionHistory: false,
          isUploadingFraReport: false,
          submissionHistory: [],
        },
      }

      const store = mockStore(state)
      const origDispatch = store.dispatch
      store.dispatch = jest.fn(origDispatch)

      const component = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      const { getByLabelText, getByText } = component

      mockAxios.get.mockResolvedValue({
        data: submissionHistoryApiResponse,
      })

      // fill out the form values before clicking search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)*')
      fireEvent.change(yearsDropdown, { target: { value: '2021' } })

      const quarterDropdown = getByLabelText('Fiscal Quarter*')
      fireEvent.change(quarterDropdown, { target: { value: 'Q1' } })

      await waitFor(() => {
        expect(
          getByText(
            'Alaska - Work Outcomes of TANF Exiters - Fiscal Year 2021 - Quarter 1 (October - December)'
          )
        ).toBeInTheDocument()
        expect(getByText('Submit Report')).toBeInTheDocument()
      })

      return { ...component, ...store }
    }

    it('Renders a message when no data is available', async () => {
      const submissionHistoryState = []

      const { getByText } = await setup(submissionHistoryState)

      await waitFor(() => {
        expect(getByText('No data available.')).toBeInTheDocument()
      })
    })

    it('Renders a table with the submission history data if available', async () => {
      const submissionHistoryApiResponse = [
        {
          id: 1,
          original_filename: 'testFile.txt',
          extension: 'txt',
          quarter: 'Q1',
          section: 'Work Outcomes of TANF Exiters',
          slug: '1234-5-6-7890',
          year: '2021',
          s3_version_id: '3210',
          created_at: '2025-02-07T23:38:58+0000',
          submitted_by: 'Test Testerson',
          has_error: false,
          summary: {
            status: 'Accepted',
            case_aggregates: {
              total_errors: 0,
            },
          },
          latest_reparse_file_meta: '',
        },
      ]

      const { getByText } = await setup(submissionHistoryApiResponse)

      await waitFor(() => {
        expect(getByText(/by Test Testerson/)).toBeInTheDocument()
        expect(
          getByText('testFile.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          within(
            getByText('Work Outcomes of TANF Exiters Submission History')
              .parentElement
          ).getByText('0')
        ).toBeInTheDocument()
        expect(getByText('Accepted')).toBeInTheDocument()
        expect(getByText('No Errors')).toBeInTheDocument()
      })
    })

    it('Renders a paginated table with a page size of 5', async () => {
      const submissionHistoryApiResponse = []

      for (var i = 0; i < 8; i++) {
        submissionHistoryApiResponse.push({
          id: i,
          original_filename: `testFile${i}.txt`,
          extension: 'txt',
          quarter: 'Q1',
          section: 'Work Outcomes of TANF Exiters',
          slug: '1234-5-6-7890',
          year: '2021',
          s3_version_id: '3210',
          created_at: '2025-02-07T23:38:58+0000',
          submitted_by: 'Test Testerson',
          has_error: false,
          summary: {
            status: 'Accepted',
            case_aggregates: {
              total_errors: 0,
            },
          },
          latest_reparse_file_meta: '',
        })
      }

      const { getByText, queryByText } = await setup(
        submissionHistoryApiResponse
      )

      await waitFor(() => {
        expect(
          getByText('testFile0.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          getByText('testFile1.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          getByText('testFile2.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          getByText('testFile3.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          getByText('testFile4.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          queryByText('testFile5.txt', { selector: 'td button' })
        ).not.toBeInTheDocument()
      })

      fireEvent.click(
        getByText(/Next/, {
          selector: 'button span',
        })
      )

      await waitFor(() => {
        expect(
          getByText('testFile5.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          getByText('testFile6.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          getByText('testFile7.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          queryByText('testFile4.txt', { selector: 'td button' })
        ).not.toBeInTheDocument()
      })
    })

    it('shows a special status for timed out status polling attempts', async () => {
      const submissionHistoryApiResponse = [
        {
          id: 1,
          original_filename: 'testFile.txt',
          extension: 'txt',
          quarter: 'Q1',
          section: 'Work Outcomes of TANF Exiters',
          slug: '1234-5-6-7890',
          year: '2021',
          s3_version_id: '3210',
          created_at: '2025-02-07T23:38:58+0000',
          submitted_by: 'Test Testerson',
          has_error: false,
          summary: {
            status: 'TimedOut',
          },
          latest_reparse_file_meta: '',
        },
      ]

      const { getByText } = await setup(submissionHistoryApiResponse)

      await waitFor(() => {
        expect(getByText(/by Test Testerson/)).toBeInTheDocument()
        expect(
          getByText('testFile.txt', { selector: 'td button' })
        ).toBeInTheDocument()
        expect(
          within(
            getByText('Work Outcomes of TANF Exiters Submission History')
              .parentElement
          ).getByText('Pending')
        ).toBeInTheDocument()
        expect(
          getByText('Still processing. Check back soon.')
        ).toBeInTheDocument()
        expect(getByText('Pending')).toBeInTheDocument()
      })
    })
  })

  describe('Form validation', () => {
    it('should show error when fiscal year field is blurred without selection', async () => {
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)
      const { getByLabelText, queryByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      const yearSelect = getByLabelText('Fiscal Year (October - September)*')

      // Blur the field without selecting a value
      fireEvent.blur(yearSelect)

      await waitFor(() => {
        expect(queryByText('A fiscal year is required')).toBeInTheDocument()
      })
    })

    it('should clear fiscal year error when a value is selected', async () => {
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)
      const { getByLabelText, queryByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      const yearSelect = getByLabelText('Fiscal Year (October - September)*')

      // Blur without selection to trigger error
      fireEvent.blur(yearSelect)

      await waitFor(() => {
        expect(queryByText('A fiscal year is required')).toBeInTheDocument()
      })

      // Select a year
      fireEvent.change(yearSelect, { target: { value: '2021' } })

      await waitFor(() => {
        expect(queryByText('A fiscal year is required')).not.toBeInTheDocument()
      })
    })

    it('should show error when fiscal quarter field is blurred without selection', async () => {
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)
      const { getByLabelText, queryByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      const quarterSelect = getByLabelText('Fiscal Quarter*')

      // Blur the field without selecting a value
      fireEvent.blur(quarterSelect)

      await waitFor(() => {
        expect(queryByText('A fiscal quarter is required')).toBeInTheDocument()
      })
    })

    it('should clear fiscal quarter error when a value is selected', async () => {
      const state = {
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
            roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
      }

      const store = mockStore(state)
      const { getByLabelText, queryByText } = render(
        <Provider store={store}>
          <MemoryRouter>
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      const quarterSelect = getByLabelText('Fiscal Quarter*')

      // Blur without selection to trigger error
      fireEvent.blur(quarterSelect)

      await waitFor(() => {
        expect(queryByText('A fiscal quarter is required')).toBeInTheDocument()
      })

      // Select a quarter
      fireEvent.change(quarterSelect, { target: { value: 'Q1' } })

      await waitFor(() => {
        expect(
          queryByText('A fiscal quarter is required')
        ).not.toBeInTheDocument()
      })
    })

    describe('Form order enforcement', () => {
      it('should not show errors when filling File Type -> Year -> Quarter in order', async () => {
        const state = {
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
              roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
              account_approval_status: 'Approved',
            },
          },
        }

        const store = mockStore(state)
        const { getByLabelText, queryByText } = render(
          <Provider store={store}>
            <MemoryRouter>
              <FRAReports />
            </MemoryRouter>
          </Provider>
        )

        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')

        // No errors should show
        expect(queryByText('A fiscal year is required')).not.toBeInTheDocument()
        expect(
          queryByText('A fiscal quarter is required')
        ).not.toBeInTheDocument()

        // Select year
        fireEvent.change(yearSelect, { target: { value: '2021' } })

        // Still no errors
        expect(
          queryByText('A fiscal quarter is required')
        ).not.toBeInTheDocument()

        // Select quarter
        fireEvent.change(quarterSelect, { target: { value: 'Q1' } })

        // No errors at any point
        expect(queryByText('A fiscal year is required')).not.toBeInTheDocument()
        expect(
          queryByText('A fiscal quarter is required')
        ).not.toBeInTheDocument()
      })

      it('should show error only on blurred field when filling in order', async () => {
        const state = {
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
              roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
              account_approval_status: 'Approved',
            },
          },
        }

        const store = mockStore(state)
        const { getByLabelText, queryByText } = render(
          <Provider store={store}>
            <MemoryRouter>
              <FRAReports />
            </MemoryRouter>
          </Provider>
        )

        const yearSelect = getByLabelText('Fiscal Year (October - September)*')

        // Blur year without selection
        fireEvent.blur(yearSelect)

        await waitFor(() => {
          expect(queryByText('A fiscal year is required')).toBeInTheDocument()
        })

        // Quarter should not show error (not touched yet)
        expect(
          queryByText('A fiscal quarter is required')
        ).not.toBeInTheDocument()
      })

      it('should show errors on all empty fields when selecting Year first', async () => {
        const state = {
          ...initialState,
          auth: {
            authenticated: true,
            user: {
              email: 'hi@bye.com',
              stt: null,
              roles: [{ id: 1, name: 'OFA System Admin', permission: [] }],
              account_approval_status: 'Approved',
            },
          },
        }

        const store = mockStore(state)
        const { getByLabelText, queryByText } = render(
          <Provider store={store}>
            <MemoryRouter>
              <FRAReports />
            </MemoryRouter>
          </Provider>
        )

        const yearSelect = getByLabelText('Fiscal Year (October - September)*')

        // Select year first (breaking order - STT not selected)
        fireEvent.change(yearSelect, { target: { value: '2021' } })

        await waitFor(() => {
          // Quarter should show error (empty and touched)
          expect(
            queryByText('A fiscal quarter is required')
          ).toBeInTheDocument()
        })

        // STT should show error (empty and touched)
        expect(
          queryByText('A state, tribe, or territory is required')
        ).toBeInTheDocument()

        // Year should not show error (has value)
        expect(queryByText('A fiscal year is required')).not.toBeInTheDocument()
      })

      it('should show errors on all empty fields when selecting Quarter first', async () => {
        const state = {
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
              roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
              account_approval_status: 'Approved',
            },
          },
        }

        const store = mockStore(state)
        const { getByLabelText, queryByText } = render(
          <Provider store={store}>
            <MemoryRouter>
              <FRAReports />
            </MemoryRouter>
          </Provider>
        )

        const quarterSelect = getByLabelText('Fiscal Quarter*')

        // Select quarter first (breaking order)
        fireEvent.change(quarterSelect, { target: { value: 'Q1' } })

        await waitFor(() => {
          // Year should show error (empty and touched)
          expect(queryByText('A fiscal year is required')).toBeInTheDocument()
        })

        // Quarter should not show error (has value)
        expect(
          queryByText('A fiscal quarter is required')
        ).not.toBeInTheDocument()
      })

      it('should not show error on fields with valid values even when order is broken', async () => {
        const state = {
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
              roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
              account_approval_status: 'Approved',
            },
          },
        }

        const store = mockStore(state)
        const { getByLabelText, queryByText } = render(
          <Provider store={store}>
            <MemoryRouter>
              <FRAReports />
            </MemoryRouter>
          </Provider>
        )

        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')

        // Fill year first
        fireEvent.change(yearSelect, { target: { value: '2021' } })

        // Then fill quarter
        fireEvent.change(quarterSelect, { target: { value: 'Q1' } })

        await waitFor(() => {
          // Neither year nor quarter should show errors (both have values)
          expect(
            queryByText('A fiscal year is required')
          ).not.toBeInTheDocument()
          expect(
            queryByText('A fiscal quarter is required')
          ).not.toBeInTheDocument()
        })
      })

      describe('Error clearing', () => {
        it('should clear error when empty field gets a value', async () => {
          const state = {
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
                roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
                account_approval_status: 'Approved',
              },
            },
          }

          const store = mockStore(state)
          const { getByLabelText, queryByText } = render(
            <Provider store={store}>
              <MemoryRouter>
                <FRAReports />
              </MemoryRouter>
            </Provider>
          )

          const yearSelect = getByLabelText(
            'Fiscal Year (October - September)*'
          )
          const quarterSelect = getByLabelText('Fiscal Quarter*')

          // Select quarter first to trigger errors
          fireEvent.change(quarterSelect, { target: { value: 'Q1' } })

          await waitFor(() => {
            expect(queryByText('A fiscal year is required')).toBeInTheDocument()
          })

          // Fill year
          fireEvent.change(yearSelect, { target: { value: '2021' } })

          await waitFor(() => {
            expect(
              queryByText('A fiscal year is required')
            ).not.toBeInTheDocument()
          })
        })
      })

      describe('Admin users with STT selection', () => {
        it('should not show errors when filling STT -> File Type -> Year -> Quarter in order', async () => {
          const state = {
            ...initialState,
            auth: {
              authenticated: true,
              user: {
                email: 'hi@bye.com',
                stt: null,
                roles: [{ id: 1, name: 'OFA System Admin', permission: [] }],
                account_approval_status: 'Approved',
              },
            },
          }

          const store = mockStore(state)
          const { getByLabelText, getByTestId, queryByText } = render(
            <Provider store={store}>
              <MemoryRouter>
                <FRAReports />
              </MemoryRouter>
            </Provider>
          )

          const sttDropdown = getByTestId('stt-combobox')
          const yearSelect = getByLabelText(
            'Fiscal Year (October - September)*'
          )
          const quarterSelect = getByLabelText('Fiscal Quarter*')

          // Select STT
          fireEvent.change(sttDropdown, { target: { value: 'Alaska' } })

          // No errors should show yet
          await waitFor(() => {
            expect(
              queryByText('A fiscal year is required')
            ).not.toBeInTheDocument()
            expect(
              queryByText('A fiscal quarter is required')
            ).not.toBeInTheDocument()
          })

          // Select year
          fireEvent.change(yearSelect, { target: { value: '2021' } })

          // Still no errors
          await waitFor(() => {
            expect(
              queryByText('A fiscal quarter is required')
            ).not.toBeInTheDocument()
          })

          // Select quarter
          fireEvent.change(quarterSelect, { target: { value: 'Q1' } })

          // No errors at any point
          await waitFor(() => {
            expect(
              queryByText('A state, tribe, or territory is required')
            ).not.toBeInTheDocument()
            expect(
              queryByText('A fiscal year is required')
            ).not.toBeInTheDocument()
            expect(
              queryByText('A fiscal quarter is required')
            ).not.toBeInTheDocument()
          })
        })
      })
    })
  })

  describe('URL parameter validation', () => {
    const adminState = {
      ...initialState,
      auth: {
        authenticated: true,
        user: {
          email: 'hi@bye.com',
          stt: null,
          roles: [{ id: 1, name: 'OFA System Admin', permission: [] }],
          account_approval_status: 'Approved',
        },
      },
    }

    it('should accept valid URL parameters', async () => {
      const store = mockStore(adminState)
      const { getByLabelText } = render(
        <Provider store={store}>
          <MemoryRouter
            initialEntries={[
              '/?fy=2023&q=Q1&type=workOutcomesOfTanfExiters&stt=Alabama',
            ]}
          >
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      await waitFor(() => {
        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')
        expect(yearSelect.value).toBe('2023')
        expect(quarterSelect.value).toBe('Q1')
      })
    })

    it('should clear only fiscal year when it is invalid', async () => {
      const store = mockStore(adminState)
      const { getByLabelText } = render(
        <Provider store={store}>
          <MemoryRouter
            initialEntries={[
              '/?fy=2019&q=Q1&type=workOutcomesOfTanfExiters&stt=Alabama',
            ]}
          >
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      await waitFor(() => {
        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')
        // Only fy should be cleared, other valid params kept
        expect(yearSelect.value).toBe('')
        expect(quarterSelect.value).toBe('Q1')
      })
    })

    it('should clear only quarter when it is invalid', async () => {
      const store = mockStore(adminState)
      const { getByLabelText } = render(
        <Provider store={store}>
          <MemoryRouter
            initialEntries={[
              '/?fy=2023&q=Q5&type=workOutcomesOfTanfExiters&stt=Alabama',
            ]}
          >
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      await waitFor(() => {
        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')
        // Only quarter should be cleared, other valid params kept
        expect(yearSelect.value).toBe('2023')
        expect(quarterSelect.value).toBe('')
      })
    })

    it('should reset file type to default when it is invalid for FRA', async () => {
      const store = mockStore(adminState)
      const { getByLabelText } = render(
        <Provider store={store}>
          <MemoryRouter
            initialEntries={['/?fy=2023&q=Q1&type=tanf&stt=Alabama']}
          >
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      await waitFor(() => {
        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')
        // Year and quarter should be kept, type resets to default
        expect(yearSelect.value).toBe('2023')
        expect(quarterSelect.value).toBe('Q1')
        // Work Outcomes radio should be selected (default for FRA)
        const workOutcomesRadio = getByLabelText(
          'Work Outcomes of TANF Exiters'
        )
        expect(workOutcomesRadio.checked).toBe(true)
      })
    })

    it('should clear only STT when it is invalid', async () => {
      const store = mockStore(adminState)
      const { getByLabelText } = render(
        <Provider store={store}>
          <MemoryRouter
            initialEntries={[
              '/?fy=2023&q=Q1&type=workOutcomesOfTanfExiters&stt=NonExistentSTT',
            ]}
          >
            <FRAReports />
          </MemoryRouter>
        </Provider>
      )

      await waitFor(() => {
        const yearSelect = getByLabelText('Fiscal Year (October - September)*')
        const quarterSelect = getByLabelText('Fiscal Quarter*')
        const sttInput = getByLabelText('State, Tribe, or Territory*', {
          selector: 'input',
        })
        // Only STT should be cleared, other valid params kept
        expect(yearSelect.value).toBe('2023')
        expect(quarterSelect.value).toBe('Q1')
        expect(sttInput.value).toBe('')
      })
    })
  })
})
