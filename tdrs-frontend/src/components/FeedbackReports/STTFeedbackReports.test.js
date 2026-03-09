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
        account_approval_status: 'Approved',
        stt: { id: 1, name: 'Alabama' },
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
        roles: [{ name: 'OFA Regional Staff', permissions: [] }],
        account_approval_status: 'Approved',
        regions: [
          {
            id: 5,
            stts: [
              { id: 10, name: 'Wisconsin', type: 'state' },
              { id: 11, name: 'Illinois', type: 'state' },
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
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select a year first
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback reports are produced cumulatively/i)
        ).toBeInTheDocument()
        expect(screen.getByText(/Yun.Song@acf.hhs.gov/i)).toBeInTheDocument()
        expect(screen.getByText(/TANFData@acf.hhs.gov/i)).toBeInTheDocument()
      })
    })

    it('renders the Knowledge Center link when year is selected', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select a year first
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Report Reference/i)
        ).toBeInTheDocument()
      })
    })

    it('renders the H2 header with STT name and fiscal year when year is selected', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select a year
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('renders the H3 heading as just "Feedback Reports" when year is selected', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select a year
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

    it('does not render Search button for Data Analyst', () => {
      renderComponent()
      expect(
        screen.queryByRole('button', { name: /Search/i })
      ).not.toBeInTheDocument()
    })
  })

  describe('Data Fetching', () => {
    it('does not fetch reports on mount when no year is selected', async () => {
      renderComponent()

      // Wait a bit to ensure no fetch happens
      await waitFor(() => {
        expect(get).not.toHaveBeenCalled()
      })
    })

    it('fetches reports when year is selected', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select a year
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025 },
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

      // Select a year to trigger fetch
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

      // Select a year to trigger fetch
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
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select a year to trigger fetch
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

      // Select a year to trigger fetch
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

      // Mock first fetch for 2025
      get.mockResolvedValueOnce({
        data: { results: mock2025Reports },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select 2025 first
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      // Wait for initial load - should show 2025 reports
      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
      })

      // Verify initial call was made with 2025
      expect(get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/'),
        expect.objectContaining({
          params: { year: 2025 },
        })
      )

      // Mock the next fetch for 2024
      get.mockResolvedValueOnce({
        data: { results: mock2024Reports },
        ok: true,
        status: 200,
        error: null,
      })

      // Change to 2024 - should automatically fetch new reports
      fireEvent.change(yearSelect, { target: { value: '2024' } })

      // Should fetch with new year param
      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2024 },
          })
        )
      })

      // Reports should now show 2024 data
      await waitFor(() => {
        expect(screen.getByText('FY2024.zip')).toBeInTheDocument()
        expect(screen.queryByText('FY2025.zip')).not.toBeInTheDocument()
      })
    })

    it('updates the H2 heading when year is changed', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select 2025 first
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      // Verify initial heading
      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })

      // Change to 2024
      fireEvent.change(yearSelect, { target: { value: '2024' } })

      // Heading should update immediately
      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — Fiscal Year 2024 Feedback Reports',
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

      // Select a year to trigger fetch
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

      // Select a year to trigger fetch
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('direct.zip')).toBeInTheDocument()
      })
    })

    it('handles response with null/empty data', async () => {
      get.mockResolvedValue({ data: null, ok: true, status: 200, error: null })

      renderComponent()

      // Select a year to trigger fetch
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

      // Select a year to trigger fetch
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(screen.getByText('report1.zip')).toBeInTheDocument()
        expect(screen.getByText('report2.zip')).toBeInTheDocument()
      })
    })
  })

  describe('URL Parameter Handling', () => {
    const renderWithUrl = (url) => {
      return render(
        <MemoryRouter initialEntries={[url]}>
          <Provider store={store}>
            <STTFeedbackReports />
          </Provider>
        </MemoryRouter>
      )
    }

    it('initializes year from URL parameter', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('2024')
      })
    })

    it('fetches reports with year from URL parameter', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2024 },
          })
        )
      })
    })

    it('shows placeholder for invalid year param', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderWithUrl('/feedback-reports?year=invalid')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('')
      })

      // Content below hr should not be visible
      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
    })

    it('shows placeholder for out-of-range year', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderWithUrl('/feedback-reports?year=1999')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('')
      })

      // Content below hr should not be visible
      expect(
        screen.queryByRole('heading', { level: 2 })
      ).not.toBeInTheDocument()
    })

    it('displays H2 heading with STT name and year from URL parameter', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Alabama — Fiscal Year 2024 Feedback Reports',
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

      // Content below hr should not be visible
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

    it('renders Search button for regional staff', () => {
      renderComponent(regionalStore)
      expect(
        screen.getByRole('button', { name: /Search/i })
      ).toBeInTheDocument()
    })

    it('Search button is disabled when no STT or year is selected', () => {
      renderComponent(regionalStore)
      const searchBtn = screen.getByRole('button', { name: /Search/i })
      expect(searchBtn).toBeDisabled()
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

    it('does not auto-fetch reports when year changes', async () => {
      renderComponent(regionalStore)

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      // Wait to ensure no fetch happens
      await waitFor(() => {
        expect(get).not.toHaveBeenCalled()
      })
    })

    it('fetches reports with stt param when Search is clicked', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent(regionalStore)

      // Select STT via mocked ComboBox
      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Wisconsin' } })

      // Select a year
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      // Search button should now be enabled
      const searchBtn = screen.getByRole('button', { name: /Search/i })
      expect(searchBtn).not.toBeDisabled()

      // Click search
      fireEvent.click(searchBtn)

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2025, stt: 10 },
          })
        )
      })
    })

    it('shows H2 heading with selected STT name after search', async () => {
      get.mockResolvedValue({
        data: { results: [] },
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

      // Content should show since both STT and year are selected
      await waitFor(() => {
        expect(
          screen.getByRole('heading', {
            level: 2,
            name: 'Wisconsin — Fiscal Year 2025 Feedback Reports',
          })
        ).toBeInTheDocument()
      })
    })

    it('clears reports when STT selection changes', async () => {
      get.mockResolvedValue({
        data: { results: [{ id: 1, year: 2025, date_extracted_on: '2025-02-28', created_at: '2025-03-05T10:41:00Z', original_filename: 'test.zip' }] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent(regionalStore)

      // Select STT and year, then search
      const sttSelect = screen.getByLabelText(/State, Tribe, or Territory/i)
      fireEvent.change(sttSelect, { target: { value: 'Wisconsin' } })

      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2025' } })

      fireEvent.click(screen.getByRole('button', { name: /Search/i }))

      await waitFor(() => {
        expect(screen.getByText('test.zip')).toBeInTheDocument()
      })

      // Change STT - reports should clear
      fireEvent.change(sttSelect, { target: { value: 'Illinois' } })

      await waitFor(() => {
        expect(screen.queryByText('test.zip')).not.toBeInTheDocument()
      })
    })
  })
})
