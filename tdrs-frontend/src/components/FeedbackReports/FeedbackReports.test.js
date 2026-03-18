import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import FeedbackReports from './FeedbackReports'
import { get } from '../../fetch-instance'

jest.mock('../../fetch-instance')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
  datePicker: {
    init: jest.fn(),
  },
  comboBox: {
    init: jest.fn(),
  },
}))

// Mock STTComboBox to avoid fetchSttList side effects
jest.mock('../STTComboBox', () => {
  const MockSTTComboBox = ({ selectStt, selectedStt }) => (
    <div data-testid="stt-combobox">
      <label htmlFor="mock-stt-select">State, Tribe, or Territory*</label>
      <select
        id="mock-stt-select"
        value={selectedStt || ''}
        onChange={(e) => selectStt(e.target.value)}
        aria-label="State, Tribe, or Territory"
      >
        <option value="">- Select or Search -</option>
        <option value="Wisconsin">Wisconsin</option>
      </select>
    </div>
  )
  MockSTTComboBox.displayName = 'MockSTTComboBox'
  return MockSTTComboBox
})

const mockStore = configureStore([thunk])

describe('FeedbackReports', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    get.mockResolvedValue({
      data: { results: [] },
      ok: true,
      status: 200,
      error: null,
    })

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
        stts: { sttList: [], loading: false },
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
        stts: { sttList: [], loading: false },
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
        stts: { sttList: [], loading: false },
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
        stts: { sttList: [], loading: false },
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
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Should render STT view since they have no upload permissions
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })
    })

    it('renders STTFeedbackReports for OFA Regional Staff (not Admin view)', async () => {
      const store = mockStore({
        auth: {
          user: {
            id: 1,
            email: 'regional@example.com',
            roles: [
              {
                name: 'OFA Regional Staff',
                permissions: [{ codename: 'view_reportfile' }],
              },
            ],
            account_approval_status: 'Approved',
            regions: [
              {
                id: 5,
                stts: [{ id: 10, name: 'Wisconsin', type: 'state' }],
              },
            ],
          },
          authenticated: true,
        },
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Should render STT view (not admin) since regional staff don't have add_reportsource
      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
      })

      // Should NOT have the Upload button
      expect(
        screen.queryByRole('button', { name: /Upload & Notify States/i })
      ).not.toBeInTheDocument()
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
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // Admin page requires fiscal year selection before API call
      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()
      })

      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
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
        stts: { sttList: [], loading: false },
      })

      renderComponent(store)

      // STT users must select a fiscal year before reports are fetched
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.any(Object)
        )
      })

      // Make sure it's not calling the report-sources endpoint
      const calls = get.mock.calls
      const reportSourcesCall = calls.find((call) =>
        call[0].includes('report-sources')
      )
      expect(reportSourcesCall).toBeUndefined()
    })
  })
})
