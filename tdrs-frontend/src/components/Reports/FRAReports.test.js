import React from 'react'
import { fireEvent, waitFor, render } from '@testing-library/react'
import axios from 'axios'
import { Provider } from 'react-redux'
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
  it('Renders', () => {
    const store = mockStore()
    const { getByText, queryByText } = render(
      <Provider store={store}>
        <FRAReports />
      </Provider>
    )

    // search form elements exist
    expect(getByText('File Type')).toBeInTheDocument()
    expect(getByText('Fiscal Year (October - September)')).toBeInTheDocument()
    expect(getByText('Quarter')).toBeInTheDocument()
    expect(
      getByText('Identifying the right Fiscal Year and Quarter')
    ).toBeInTheDocument()
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

      const { getByText, queryByText } = render(
        <Provider store={store}>
          <FRAReports />
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
          <FRAReports />
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
          <FRAReports />
        </Provider>
      )

      expect(
        queryByText('Associated State, Tribe, or Territory*')
      ).not.toBeInTheDocument()
      expect(getByText('An STT is not set for this user.')).toBeInTheDocument()
    })

    it('Shows errors if required values are not set', () => {
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

      const { getByText, queryByText } = render(
        <Provider store={store}>
          <FRAReports />
        </Provider>
      )

      // don't fill out any form values
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      // upload form not displayed
      expect(queryByText('Submit Report')).not.toBeInTheDocument()

      // fields all have errors
      expect(
        getByText('A state, tribe, or territory is required')
      ).toBeInTheDocument()
      expect(getByText('A fiscal year is required')).toBeInTheDocument()
      expect(getByText('A quarter is required')).toBeInTheDocument()
      expect(getByText('There are 3 error(s) in this form')).toBeInTheDocument()
    })

    it('Updates form validation if values are changed', async () => {
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

      const { getByText, queryByText, getByLabelText } = render(
        <Provider store={store}>
          <FRAReports />
        </Provider>
      )

      // don't fill out any form values
      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      // upload form not displayed
      expect(queryByText('Submit Report')).not.toBeInTheDocument()

      // fields all have errors
      expect(
        getByText('A state, tribe, or territory is required')
      ).toBeInTheDocument()
      expect(getByText('A fiscal year is required')).toBeInTheDocument()
      expect(getByText('A quarter is required')).toBeInTheDocument()
      expect(getByText('There are 3 error(s) in this form')).toBeInTheDocument()

      const yearsDropdown = getByLabelText(
        'Fiscal Year (October - September)',
        { exact: false }
      )
      fireEvent.change(yearsDropdown, { target: { value: '2021' } })

      await waitFor(() => {
        expect(queryByText('A fiscal year is required')).not.toBeInTheDocument()
        expect(
          getByText('There are 2 error(s) in this form')
        ).toBeInTheDocument()
      })

      const quarterDropdown = getByLabelText('Quarter', { exact: false })
      fireEvent.change(quarterDropdown, { target: { value: 'Q1' } })

      await waitFor(() => {
        expect(queryByText('A quarter is required')).not.toBeInTheDocument()
        expect(
          getByText('There is 1 error(s) in this form')
        ).toBeInTheDocument()
      })
    })

    it('Shows upload form once search has been clicked', async () => {
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
          <FRAReports />
        </Provider>
      )

      // fill out the form values before clicking search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)')
      fireEvent.change(yearsDropdown, { target: { value: '2021' } })

      const quarterDropdown = getByLabelText('Quarter')
      fireEvent.change(quarterDropdown, { target: { value: 'Q1' } })

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      // upload form displayed
      await waitFor(() => {
        expect(
          getByText(
            'Alaska - Work Outcomes of TANF Exiters - Fiscal Year 2021 - Quarter 1 (October - December)'
          )
        ).toBeInTheDocument()
        expect(getByText('Submit Report')).toBeInTheDocument()
      })

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

      const component = render(
        <Provider store={store}>
          <FRAReports />
        </Provider>
      )

      const { getByLabelText, getByText } = component

      // fill out the form values before clicking search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)')
      fireEvent.change(yearsDropdown, { target: { value: '2021' } })

      const quarterDropdown = getByLabelText('Quarter')
      fireEvent.change(quarterDropdown, { target: { value: 'Q1' } })

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

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

      return { ...component, ...store }
    }

    it('Allows text files to be selected and submitted', async () => {
      const { getByText, dispatch, getByRole, container } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.txt. To change the selected file, click this button.'
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
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(2))
    })

    it('Shows an error if file submission failed', async () => {
      jest.mock('axios')
      const mockAxios = axios
      const { getByText, dispatch, getByRole, container } = await setup()

      mockAxios.post.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.txt. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      const submitButton = getByText('Submit Report')
      fireEvent.click(submitButton)

      await waitFor(() =>
        expect(getByText('Error: Mock fail response')).toBeInTheDocument()
      )
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(2))
    })

    it('Shows an error if a no file is selected for submission', async () => {
      const { getByText, dispatch, getByRole, container } = await setup()

      const submitButton = getByText('Submit Report', { selector: 'button' })
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(
          getByText('No changes have been made to data files')
        ).toBeInTheDocument()
      })
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
            'Invalid extension. Accepted file types are: .txt, .ms##, .ts##, or .ts###.'
          )
        ).toBeInTheDocument()
      })

      const submitButton = getByText('Submit Report', { selector: 'button' })
      fireEvent.click(submitButton)

      await waitFor(() => getByRole('alert'))
      expect(dispatch).toHaveBeenCalledTimes(1)
    })

    it('Shows a message if search is clicked with an non-uploaded file', async () => {
      const { getByText, container, getByLabelText, queryByText } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })

      await waitFor(() => {
        expect(
          getByText('You have selected the file: report.txt')
        ).toBeInTheDocument()
      })

      const yearsDropdown = getByLabelText('Fiscal Year (October - September)')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      const quarterDropdown = getByLabelText('Quarter')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })

      await waitFor(() => {
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )
    })

    it('Cancels the upload if Cancel is clicked', async () => {
      const { getByText, container, queryByText } = await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })

      await waitFor(() => {
        expect(
          getByText('You have selected the file: report.txt')
        ).toBeInTheDocument()
      })

      fireEvent.click(getByText(/Cancel/, { selector: 'button' }))

      await waitFor(() => {
        expect(
          queryByText('You have selected the file: report.txt')
        ).not.toBeInTheDocument()
        expect(queryByText(/Submit Report/)).not.toBeInTheDocument()
      })
    })

    it('Does not show a message if search is clicked after uploading a file', async () => {
      const { getByText, container, getByLabelText, queryByText, dispatch } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.txt. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      fireEvent.click(getByText(/Submit Report/, { selector: 'button' }))
      await waitFor(() => expect(dispatch).toHaveBeenCalledTimes(2))

      const yearsDropdown = getByLabelText('Fiscal Year (October - September)')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      const quarterDropdown = getByLabelText('Quarter')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })

      await waitFor(() => {
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).not.toBeInTheDocument()
      )
    })

    it('Allows the user to cancel the error modal and retain previous search selections', async () => {
      const { getByText, queryByText, getByLabelText, container, dispatch } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.txt. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      // make a change to the search selections and click search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      const quarterDropdown = getByLabelText('Quarter')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })
      await waitFor(() => {
        expect(getByText('2024', { selector: 'option' }).selected).toBe(true)
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      // click cancel
      fireEvent.click(getByText(/Cancel/, { selector: '#modal button' }))

      // assert file still exists, search params are the same as initial, dispatch not called
      await waitFor(() => {
        expect(dispatch).toHaveBeenCalledTimes(1)
        expect(queryByText('Files Not Submitted')).not.toBeInTheDocument()
        expect(
          getByText(
            'Selected File report.txt. To change the selected file, click this button.'
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
      const { getByText, queryByText, getByLabelText, container, dispatch } =
        await setup()

      const uploadForm = container.querySelector('#fra-file-upload')
      fireEvent.change(uploadForm, {
        target: { files: [makeTestFile('report.txt')] },
      })
      await waitFor(() =>
        expect(
          getByText(
            'Selected File report.txt. To change the selected file, click this button.'
          )
        ).toBeInTheDocument()
      )

      // make a change to the search selections and click search
      const yearsDropdown = getByLabelText('Fiscal Year (October - September)')
      fireEvent.change(yearsDropdown, { target: { value: '2024' } })

      const quarterDropdown = getByLabelText('Quarter')
      fireEvent.change(quarterDropdown, { target: { value: 'Q2' } })
      await waitFor(() => {
        expect(getByText('2024', { selector: 'option' }).selected).toBe(true)
        expect(
          getByText('Quarter 2 (January - March)', { selector: 'option' })
            .selected
        ).toBe(true)
      })

      fireEvent.click(getByText(/Search/, { selector: 'button' }))

      await waitFor(() =>
        expect(queryByText('Files Not Submitted')).toBeInTheDocument()
      )

      // click discard
      const button = getByText(/Discard and Search/, {
        selector: '#modal button',
      })
      fireEvent.click(button)

      // assert file discarded, search params updated
      await waitFor(() => {
        // expect(dispatch).toHaveBeenCalledTimes(2)
        expect(queryByText('Files Not Submitted')).not.toBeInTheDocument()
        expect(
          queryByText(
            'Selected File report.txt. To change the selected file, click this button.'
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
})
