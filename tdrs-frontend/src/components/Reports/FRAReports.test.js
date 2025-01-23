import React from 'react'
import { FRAReports } from '.'
import { fireEvent, waitFor, render } from '@testing-library/react'
import configureStore from '../../configureStore'
import { Provider } from 'react-redux'

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
    expect(getByText('Work Outcomes for TANF Exiters')).toBeInTheDocument()

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

      expect(
        getByText('Associated State, Tribe, or Territory*')
      ).toBeInTheDocument()
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
            'Alaska - Work Outcomes for TANF Exiters - Fiscal Year 2021 - Quarter 1 (October - December)'
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
    it('Allows text files to be selected and submitted', () => {})

    it('Shows an error if a non-allowed file type is selected', () => {})

    it('Shows a message if search is clicked with an non-uploaded file', () => {})

    it('Does not show a message if search is clicked after uploading a file', () => {})
  })
})
