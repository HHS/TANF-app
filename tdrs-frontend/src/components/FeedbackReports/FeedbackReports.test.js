import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import FeedbackReports from './FeedbackReports'
import axiosInstance from '../../axios-instance'

jest.mock('../../axios-instance')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
  datePicker: {
    init: jest.fn(),
  },
}))

const mockStore = configureStore([thunk])

describe('FeedbackReports', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    axiosInstance.get.mockResolvedValue({ data: { results: [] } })

    // Mock FileReader for AdminFeedbackReports
    global.FileReader = jest.fn().mockImplementation(() => ({
      readAsArrayBuffer: jest.fn(function () {
        setTimeout(() => this.onload && this.onload(), 0)
      }),
      result: new ArrayBuffer(8),
    }))
  })

  const renderComponent = (store) => {
    return render(
      <MemoryRouter>
        <Provider store={store}>
          <FeedbackReports />
        </Provider>
      </MemoryRouter>
    )
  }

  describe('Conditional Rendering', () => {
    it('renders AdminFeedbackReports for users with upload permissions', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'admin@example.com',
            roles: [
              {
                name: 'DIGIT Team',
                permissions: [
                  { codename: 'view_reportsource' },
                  { codename: 'add_reportsource' },
                ],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // AdminFeedbackReports has the description and fiscal year selector
      await waitFor(() => {
        expect(
          screen.getByText(/Once submitted, TDP will distribute/)
        ).toBeInTheDocument()
      })

      // Should have the fiscal year selector (Admin page requires year selection)
      expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()

      // Select a fiscal year to reveal the upload section
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      // Now the file upload input should be visible
      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      // Should have the upload button
      expect(
        screen.getByRole('button', { name: /Upload & Notify States/i })
      ).toBeInTheDocument()
    })

    it('renders STTFeedbackReports for users without upload permissions', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'analyst@example.com',
            roles: [
              {
                name: 'Data Analyst',
                permissions: [{ codename: 'view_reportfile' }],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // STTFeedbackReports has the fiscal year selector and reference table
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })

      // Should have the fiscal year selector
      expect(
        screen.getByLabelText(/Fiscal Year \(October - September\)/i)
      ).toBeInTheDocument()

      // Should NOT have the Upload button (that's for OFA admins only)
      expect(
        screen.queryByRole('button', { name: /Upload & Notify States/i })
      ).not.toBeInTheDocument()
    })

    it('renders STTFeedbackReports for users with only view_reportsource (no add)', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'viewer@example.com',
            roles: [
              {
                name: 'Viewer',
                permissions: [{ codename: 'view_reportsource' }],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // Should render STT view since they don't have add_reportsource
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })

    it('renders STTFeedbackReports for users with only add_reportsource (no view)', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'adder@example.com',
            roles: [
              {
                name: 'Adder',
                permissions: [{ codename: 'add_reportsource' }],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // Should render STT view since they don't have view_reportsource
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })

    it('renders STTFeedbackReports for users with no permissions', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'noperm@example.com',
            roles: [{ name: 'User', permissions: [] }],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // Should render STT view since they have no upload permissions
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })
  })

  describe('Permission-based API calls', () => {
    it('calls report-sources API for admin users after fiscal year selected', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'admin@example.com',
            roles: [
              {
                name: 'DIGIT Team',
                permissions: [
                  { codename: 'view_reportsource' },
                  { codename: 'add_reportsource' },
                ],
              },
            ],
            account_approval_status: 'Approved',
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // Admin page requires fiscal year selection before API call
      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()
      })

      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/report-sources/'),
          expect.objectContaining({
            params: { year: '2025' },
          })
        )
      })
    })

    it('calls reports API for STT users after fiscal year selected', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'analyst@example.com',
            roles: [
              {
                name: 'Data Analyst',
                permissions: [{ codename: 'view_reportfile' }],
              },
            ],
            account_approval_status: 'Approved',
            stt: { id: 1, name: 'Alabama' },
          },
          authenticated: true,
        },
      })

      renderComponent(store)

      // STT users must select a fiscal year before reports are fetched
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.any(Object)
        )
      })

      // Make sure it's not calling the report-sources endpoint
      const calls = axiosInstance.get.mock.calls
      const reportSourcesCall = calls.find((call) =>
        call[0].includes('report-sources')
      )
      expect(reportSourcesCall).toBeUndefined()
    })
  })
})
