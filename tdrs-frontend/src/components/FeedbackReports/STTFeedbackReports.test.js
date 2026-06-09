import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import STTFeedbackReports from './STTFeedbackReports'
import { get } from '../../fetch-instance'

jest.mock('../../fetch-instance')

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
        <option value="Illinois">Illinois</option>
        <option value="Ho-Chunk Nation">Ho-Chunk Nation</option>
      </select>
    </div>
  )
  MockSTTComboBox.displayName = 'MockSTTComboBox'
  return MockSTTComboBox
})

const mockStore = configureStore([thunk])

const dataAnalystStore = () =>
  mockStore({
    auth: {
      user: {
        id: 1,
        email: 'analyst@example.com',
        roles: [{ name: 'Data Analyst', permissions: [] }],
        permissions: [],
        account_approval_status: 'Approved',
        stt: { id: 1, name: 'Alabama' },
      },
      authenticated: true,
    },
    stts: { sttList: [], loading: false },
  })

const tribeDataAnalystStore = () =>
  mockStore({
    auth: {
      user: {
        id: 1,
        email: 'analyst@example.com',
        roles: [{ name: 'Data Analyst', permissions: [] }],
        permissions: [],
        account_approval_status: 'Approved',
        stt: { id: 100, name: 'Ho-Chunk Nation', type: 'tribe' },
      },
      authenticated: true,
    },
    stts: { sttList: [], loading: false },
  })

const regionalStaffStore = () =>
  mockStore({
    auth: {
      user: {
        id: 2,
        email: 'regional@example.com',
        roles: [
          {
            name: 'OFA Regional Staff',
            permissions: [{ codename: 'has_fra_access' }],
          },
        ],
        permissions: [],
        account_approval_status: 'Approved',
        regions: [
          {
            id: 5,
            stts: [
              { id: 10, name: 'Wisconsin', type: 'state' },
              { id: 11, name: 'Illinois', type: 'state' },
              { id: 12, name: 'Ho-Chunk Nation', type: 'tribe' },
            ],
          },
        ],
      },
      authenticated: true,
    },
    stts: { sttList: [], loading: false },
  })

describe('STTFeedbackReports', () => {
  let store

  beforeEach(() => {
    store = dataAnalystStore()

    // Reset all mocks before each test
    jest.clearAllMocks()

    // Mock successful reports fetch by default
    get.mockResolvedValue({
      data: { results: [] },
      ok: true,
      status: 200,
      error: null,
    })
  })

  const renderComponent = (overrideStore) => {
    return render(
      <MemoryRouter>
        <Provider store={overrideStore || store}>
          <STTFeedbackReports />
        </Provider>
      </MemoryRouter>
    )
  }

  describe('Component Rendering', () => {
    it('renders the fiscal year selector with placeholder', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByLabelText(/Fiscal Year \(October - September\)/i)
        ).toBeInTheDocument()
        expect(screen.getByText('- Select Fiscal Year -')).toBeInTheDocument()
      })
    })

    it('renders the reference table', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText('TANF/SSP Data Reporting Reference')
        ).toBeInTheDocument()
        expect(screen.getByText('FY Q1')).toBeInTheDocument()
        expect(screen.getByText('FY Q2')).toBeInTheDocument()
        expect(screen.getByText('FY Q3')).toBeInTheDocument()
        expect(screen.getByText('FY Q4')).toBeInTheDocument()
      })
    })

    it('hides content below hr until fiscal year is selected', async () => {
      renderComponent()

      // Content should not be visible initially (no year selected)
      expect(
        screen.queryByText(/Feedback reports are produced cumulatively/i)
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('heading', { name: 'Feedback Reports' })
      ).not.toBeInTheDocument()

      // Select a year
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      // Now content should be visible
      await waitFor(() => {
        expect(
          screen.getByText(/Feedback reports are produced cumulatively/i)
        ).toBeInTheDocument()
      })
    })

    it('renders the description text with email links when year is selected', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback reports are produced cumulatively/i)
        ).toBeInTheDocument()
        expect(screen.getByText(/TANFData@acf.hhs.gov/i)).toBeInTheDocument()
      })
    })

    it('renders the Knowledge Center link when year is selected', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Report Reference/i)
        ).toBeInTheDocument()
      })
    })

    it('renders the H2 header with STT name, report type, and fiscal year', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — TANF/SSP Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('renders the H3 heading as just "Feedback Reports" when year is selected', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', { level: 3, name: 'Feedback Reports' })
        ).toBeInTheDocument()
      })
    })

    it('does not render STT ComboBox for Data Analyst', () => {
      renderComponent()
      expect(
        screen.queryByLabelText(/State, Tribe, or Territory/i)
      ).not.toBeInTheDocument()
    })
  })

  describe('Report Type Selection', () => {
    it('shows radio selector for non-tribe Data Analysts', () => {
      renderComponent() // dataAnalystStore has state STT

      expect(screen.getByText('Feedback Report Type*')).toBeInTheDocument()
      expect(screen.getByLabelText('TANF/SSP')).toBeInTheDocument()
      expect(screen.getByLabelText('FRA')).toBeInTheDocument()
      expect(screen.queryByLabelText('Tribal TANF')).not.toBeInTheDocument()
    })

    it('does not show radio selector for tribe Data Analysts', () => {
      renderComponent(tribeDataAnalystStore())

      expect(
        screen.queryByText('Feedback Report Type*')
      ).not.toBeInTheDocument()
    })

    it('shows Tribal TANF reference table for tribe Data Analysts', () => {
      renderComponent(tribeDataAnalystStore())

      expect(
        screen.getByText('Tribal TANF Data Reporting Reference')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('TANF/SSP Data Reporting Reference')
      ).not.toBeInTheDocument()
    })

    it('uses Tribal TANF heading for tribe Data Analysts', async () => {
      renderComponent(tribeDataAnalystStore())

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Ho-Chunk Nation — Tribal TANF Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('defaults to TANF/SSP', () => {
      renderComponent()

      expect(screen.getByLabelText('TANF/SSP')).toBeChecked()
    })

    it('updates reference table when FRA is selected', async () => {
      renderComponent()

      // Default shows TANF/SSP reference
      expect(
        screen.getByText('TANF/SSP Data Reporting Reference')
      ).toBeInTheDocument()

      // Switch to FRA
      fireEvent.click(screen.getByLabelText('FRA'))

      expect(
        screen.getByText('FRA Data Reporting Reference')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('TANF/SSP Data Reporting Reference')
      ).not.toBeInTheDocument()
    })

    it('updates header when FRA is selected', async () => {
      renderComponent()

      // Select year
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — TANF/SSP Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })

      // Switch to FRA
      fireEvent.click(screen.getByLabelText('FRA'))

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — FRA Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('fetches reports with report_type when type changes', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, report_type: 'TANF_SSP' },
          })
        )
      })

      get.mockClear()

      // Switch to FRA
      fireEvent.click(screen.getByLabelText('FRA'))

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, report_type: 'FRA' },
          })
        )
      })
    })

    it('uses TRIBAL_TANF for tribe users despite FRA URL param', async () => {
      render(
        <MemoryRouter initialEntries={['/feedback-reports?type=FRA&year=2025']}>
          <Provider store={tribeDataAnalystStore()}>
            <STTFeedbackReports />
          </Provider>
        </MemoryRouter>
      )

      // Should not show radio selector
      expect(
        screen.queryByText('Feedback Report Type*')
      ).not.toBeInTheDocument()

      // Should fetch as TRIBAL_TANF despite URL param
      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, report_type: 'TRIBAL_TANF' },
          })
        )
      })
    })

    it('fetches TRIBAL_TANF reports for tribe Data Analysts by default', async () => {
      renderComponent(tribeDataAnalystStore())

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, report_type: 'TRIBAL_TANF' },
          })
        )
      })
    })

    it('initializes report type from URL param for non-tribe users', () => {
      render(
        <MemoryRouter initialEntries={['/feedback-reports?type=FRA']}>
          <Provider store={dataAnalystStore()}>
            <STTFeedbackReports />
          </Provider>
        </MemoryRouter>
      )

      expect(screen.getByLabelText('FRA')).toBeChecked()
    })

    it('regional staff sees radio selector', () => {
      renderComponent(regionalStaffStore())

      expect(screen.getByText('Feedback Report Type*')).toBeInTheDocument()
      expect(screen.getByLabelText('TANF/SSP')).toBeInTheDocument()
      expect(screen.getByLabelText('FRA')).toBeInTheDocument()
      expect(screen.queryByLabelText('Tribal TANF')).not.toBeInTheDocument()
    })
  })

  describe('Data Fetching', () => {
    it('does not fetch reports on mount when no year is selected', async () => {
      renderComponent()

      await waitFor(() => {
        expect(get).not.toHaveBeenCalled()
      })
    })

    it('fetches reports with report_type when year is selected', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, report_type: 'TANF_SSP' },
          })
        )
      })
    })

    it('displays loading state while fetching', async () => {
      get.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  data: { results: [] },
                  ok: true,
                  status: 200,
                  error: null,
                }),
              100
            )
          )
      )

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText('Loading feedback reports...')
        ).toBeInTheDocument()
      })
    })

    it('displays error alert when fetch fails', async () => {
      get.mockResolvedValue({
        data: null,
        ok: false,
        status: 500,
        error: new Error('Failed to fetch'),
      })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(
            'Failed to load feedback reports. Please refresh the page.'
          )
        ).toBeInTheDocument()
      })
    })

    it('displays empty state when no reports exist', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(
            'No feedback reports available for this fiscal year.'
          )
        ).toBeInTheDocument()
      })
    })

    it('displays reports when data is returned', async () => {
      const mockReports = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      get.mockResolvedValue({
        data: { results: mockReports },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('F33.zip')).toBeInTheDocument()
        expect(screen.getByText('02/28/2025')).toBeInTheDocument()
      })
    })
  })

  describe('Year Filtering', () => {
    it('fetches reports automatically when year is changed', async () => {
      const mock2025Reports = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
        },
      ]

      const mock2024Reports = [
        {
          id: 2,
          year: 2024,
          date_extracted_on: '2024-09-30',
          created_at: '2024-11-08T09:48:00Z',
          original_filename: 'FY2024.zip',
        },
      ]

      get.mockResolvedValueOnce({
        data: { results: mock2025Reports },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
      })

      expect(get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/'),
        expect.objectContaining({
          params: { year: 2025, report_type: 'TANF_SSP' },
        })
      )

      get.mockResolvedValueOnce({
        data: { results: mock2024Reports },
        ok: true,
        status: 200,
        error: null,
      })

      fireEvent.change(yearSelect, { target: { value: '2024' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2024, report_type: 'TANF_SSP' },
          })
        )
      })

      await waitFor(() => {
        expect(screen.getByText('FY2024.zip')).toBeInTheDocument()
        expect(screen.queryByText('FY2025.zip')).not.toBeInTheDocument()
      })
    })

    it('updates the H2 heading when year is changed', async () => {
      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — TANF/SSP Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })

      fireEvent.change(yearSelect, { target: { value: '2024' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — TANF/SSP Fiscal Year 2024 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })
  })

  describe('Paginated Response Handling', () => {
    it('handles response with results array', async () => {
      const mockReports = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      get.mockResolvedValue({
        data: { results: mockReports },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('test.zip')).toBeInTheDocument()
      })
    })

    it('handles response with direct array', async () => {
      const mockReports = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'direct.zip',
        },
      ]

      get.mockResolvedValue({
        data: mockReports,
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('direct.zip')).toBeInTheDocument()
      })
    })

    it('handles response with null/empty data', async () => {
      get.mockResolvedValue({ data: null, ok: true, status: 200, error: null })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(
            'No feedback reports available for this fiscal year.'
          )
        ).toBeInTheDocument()
      })
    })
  })

  describe('Multiple Reports Display', () => {
    it('displays multiple reports for the same year', async () => {
      const mockReports = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-03-31',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'report1.zip',
        },
        {
          id: 2,
          year: 2025,
          date_extracted_on: '2025-01-31',
          created_at: '2025-01-08T09:48:00Z',
          original_filename: 'report2.zip',
        },
      ]

      get.mockResolvedValue({
        data: { results: mockReports },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('report1.zip')).toBeInTheDocument()
        expect(screen.getByText('report2.zip')).toBeInTheDocument()
      })
    })
  })

  describe('URL Parameter Handling', () => {
    const renderWithUrl = (url, overrideStore) => {
      return render(
        <MemoryRouter initialEntries={[url]}>
          <Provider store={overrideStore || store}>
            <STTFeedbackReports />
          </Provider>
        </MemoryRouter>
      )
    }

    it('initializes year from URL parameter', async () => {
      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('2024')
      })
    })

    it('fetches reports with year and report_type from URL parameter', async () => {
      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2024, report_type: 'TANF_SSP' },
          })
        )
      })
    })

    it('shows placeholder for invalid year param', async () => {
      renderWithUrl('/feedback-reports?year=invalid')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('')
      })

      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
    })

    it('shows placeholder for out-of-range year', async () => {
      renderWithUrl('/feedback-reports?year=1999')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('')
      })

      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
    })

    it('displays H2 heading with STT name, report type, and year from URL', async () => {
      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — TANF/SSP Fiscal Year 2024 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('shows placeholder when no year param is provided', async () => {
      renderWithUrl('/feedback-reports')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('')
      })

      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
    })
  })

  describe('Regional Staff', () => {
    let regionalStore

    beforeEach(() => {
      regionalStore = regionalStaffStore()
    })

    it('renders STT ComboBox for regional staff', () => {
      renderComponent(regionalStore)
      expect(
        screen.getByLabelText(/State, Tribe, or Territory/i)
      ).toBeInTheDocument()
    })

    it('does not show content section until both STT and year are selected', () => {
      renderComponent(regionalStore)

      // Select year only - content should not show
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
    })

    it('does not fetch reports when only year is selected', async () => {
      renderComponent(regionalStore)

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      // Wait to ensure no fetch happens (no STT selected)
      await waitFor(() => {
        expect(get).not.toHaveBeenCalled()
      })
    })

    it('auto-fetches reports with stt and report_type when both STT and year are selected', async () => {
      renderComponent(regionalStore)

      // Select STT via mocked ComboBox
      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Wisconsin' } })

      // Select a year
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, stt: 10, report_type: 'TANF_SSP' },
          })
        )
      })
    })

    it('auto-fetches Tribal TANF reports when a tribal STT and year are selected', async () => {
      renderComponent(regionalStore)

      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Ho-Chunk Nation' } })

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, stt: 12, report_type: 'TRIBAL_TANF' },
          })
        )
      })
    })

    it('shows H2 heading with selected STT name and report type', async () => {
      renderComponent(regionalStore)

      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Wisconsin' } })

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Wisconsin — TANF/SSP Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('shows Tribal TANF heading when a tribal STT is selected', async () => {
      renderComponent(regionalStore)

      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Ho-Chunk Nation' } })

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Ho-Chunk Nation — Tribal TANF Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('clears reports when STT selection changes', async () => {
      get.mockResolvedValue({
        data: {
          results: [
            {
              id: 1,
              year: 2025,
              date_extracted_on: '2025-02-28',
              created_at: '2025-03-05T10:41:00Z',
              original_filename: 'test.zip',
            },
          ],
        },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent(regionalStore)

      // Select STT and year
      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Wisconsin' } })

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('test.zip')).toBeInTheDocument()
      })

      // Change STT - reports should clear
      fireEvent.change(sttSelect, { target: { value: 'Illinois' } })

      await waitFor(() => {
        expect(screen.queryByText('test.zip')).not.toBeInTheDocument()
      })
    })

    it('initializes STT from URL stt query param', () => {
      render(
        <MemoryRouter
          initialEntries={['/feedback-reports?year=2025&stt=Wisconsin']}
        >
          <Provider store={regionalStore}>
            <STTFeedbackReports />
          </Provider>
        </MemoryRouter>
      )

      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      expect(sttSelect.value).toBe('Wisconsin')
    })

    it('hides report type selector when a tribe is selected', () => {
      renderComponent(regionalStore)

      // Initially radio should be visible (no STT selected yet)
      expect(screen.getByText('Feedback Report Type*')).toBeInTheDocument()

      // Select a tribe
      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Ho-Chunk Nation' } })

      // Radio should be hidden
      expect(
        screen.queryByText('Feedback Report Type*')
      ).not.toBeInTheDocument()
      expect(
        screen.getByText('Tribal TANF Data Reporting Reference')
      ).toBeInTheDocument()
    })

    it('shows radio again when switching from tribe to state STT', async () => {
      renderComponent(regionalStore)

      // Select a tribe — radio should hide
      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Ho-Chunk Nation' } })

      await waitFor(() => {
        expect(
          screen.queryByText('Feedback Report Type*')
        ).not.toBeInTheDocument()
      })

      // Select a state — radio should reappear with TANF_SSP selected
      fireEvent.change(sttSelect, { target: { value: 'Wisconsin' } })

      await waitFor(() => {
        expect(screen.getByText('Feedback Report Type*')).toBeInTheDocument()
        expect(screen.getByLabelText('TANF/SSP')).toBeChecked()
      })
    })

    it('initializes tribal STT from URL with TRIBAL_TANF report type', async () => {
      render(
        <MemoryRouter
          initialEntries={[
            '/feedback-reports?year=2025&stt=Ho-Chunk%20Nation&type=FRA',
          ]}
        >
          <Provider store={regionalStore}>
            <STTFeedbackReports />
          </Provider>
        </MemoryRouter>
      )

      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      expect(sttSelect.value).toBe('Ho-Chunk Nation')

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, stt: 12, report_type: 'TRIBAL_TANF' },
          })
        )
      })
    })
  })
})
