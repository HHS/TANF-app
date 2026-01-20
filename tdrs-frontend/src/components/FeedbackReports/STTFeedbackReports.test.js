import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import STTFeedbackReports from './STTFeedbackReports'
import axiosInstance from '../../axios-instance'

jest.mock('../../axios-instance')

const mockStore = configureStore([thunk])

describe('STTFeedbackReports', () => {
  let store

  beforeEach(() => {
    store = mockStore({
      auth: {
        user: {
          id: 1,
          email: 'analyst@example.com',
          roles: [{ name: 'Data Analyst', permissions: [] }],
          account_approval_status: 'Approved',
        },
        authenticated: true,
      },
    })

    // Reset all mocks before each test
    jest.clearAllMocks()

    // Mock successful reports fetch by default
    axiosInstance.get.mockResolvedValue({ data: { results: [] } })
  })

  const renderComponent = () => {
    return render(
      <MemoryRouter>
        <Provider store={store}>
          <STTFeedbackReports />
        </Provider>
      </MemoryRouter>
    )
  }

  describe('Component Rendering', () => {
    it('renders the fiscal year selector', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByLabelText(/Fiscal Year \(October - September\)/i)
        ).toBeInTheDocument()
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

    it('renders the description text with email links', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback reports are produced cumulatively/i)
        ).toBeInTheDocument()
        expect(screen.getByText(/Yun.Song@acf.hhs.gov/i)).toBeInTheDocument()
        expect(screen.getByText(/TANFData@acf.hhs.gov/i)).toBeInTheDocument()
      })
    })

    it('renders the Knowledge Center link', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Report Reference/i)
        ).toBeInTheDocument()
      })
    })

    it('renders the fiscal year heading with selected year', async () => {
      renderComponent()

      await waitFor(() => {
        const currentYear =
          new Date().getMonth() > 8
            ? new Date().getFullYear() + 1
            : new Date().getFullYear()
        expect(
          screen.getByText(`Fiscal Year ${currentYear} Feedback Reports`)
        ).toBeInTheDocument()
      })
    })
  })

  describe('Data Fetching', () => {
    it('fetches reports on mount with year param', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()

      renderComponent()

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: currentYear },
            withCredentials: true,
          })
        )
      })
    })

    it('displays loading state while fetching', () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      renderComponent()

      expect(
        screen.getByText('Loading feedback reports...')
      ).toBeInTheDocument()
    })

    it('displays error alert when fetch fails', async () => {
      axiosInstance.get.mockRejectedValue(new Error('Failed to fetch'))

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(
            'Failed to load feedback reports. Please refresh the page.'
          )
        ).toBeInTheDocument()
      })
    })

    it('displays empty state when no reports exist', async () => {
      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(
            'No feedback reports available for this fiscal year.'
          )
        ).toBeInTheDocument()
      })
    })

    it('displays reports when data is returned', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()
      const mockReports = [
        {
          id: 1,
          year: currentYear,
          quarter: 'Q1',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockReports } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('F33.zip')).toBeInTheDocument()
        expect(screen.getByText('Q1')).toBeInTheDocument()
      })
    })
  })

  describe('Year Filtering', () => {
    it('fetches reports automatically when year is changed', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()

      const mockCurrentYearReports = [
        {
          id: 1,
          year: currentYear,
          quarter: 'Q1',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'FYCurrent.zip',
        },
      ]

      const mock2024Reports = [
        {
          id: 2,
          year: 2024,
          quarter: 'Q4',
          created_at: '2024-11-08T09:48:00Z',
          original_filename: 'FY2024.zip',
        },
      ]

      // Mock initial fetch for current year
      axiosInstance.get.mockResolvedValueOnce({
        data: { results: mockCurrentYearReports },
      })

      renderComponent()

      // Wait for initial load - should show current year's reports
      await waitFor(() => {
        expect(screen.getByText('FYCurrent.zip')).toBeInTheDocument()
      })

      // Verify initial call was made with current year
      expect(axiosInstance.get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/'),
        expect.objectContaining({
          params: { year: currentYear },
        })
      )

      // Mock the next fetch for 2024
      axiosInstance.get.mockResolvedValueOnce({
        data: { results: mock2024Reports },
      })

      // Change to 2024 - should automatically fetch new reports
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2024' } })

      // Should fetch with new year param
      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: '2024' },
          })
        )
      })

      // Reports should now show 2024 data
      await waitFor(() => {
        expect(screen.getByText('FY2024.zip')).toBeInTheDocument()
        expect(screen.queryByText('FYCurrent.zip')).not.toBeInTheDocument()
      })
    })

    it('updates the heading when year is changed', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()

      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderComponent()

      // Verify initial heading
      await waitFor(() => {
        expect(
          screen.getByText(`Fiscal Year ${currentYear} Feedback Reports`)
        ).toBeInTheDocument()
      })

      // Change to 2024
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2024' } })

      // Heading should update immediately
      await waitFor(() => {
        expect(
          screen.getByText('Fiscal Year 2024 Feedback Reports')
        ).toBeInTheDocument()
      })
    })
  })

  describe('Paginated Response Handling', () => {
    it('handles response with results array', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()
      const mockReports = [
        {
          id: 1,
          year: currentYear,
          quarter: 'Q2',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockReports } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('test.zip')).toBeInTheDocument()
      })
    })

    it('handles response with direct array', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()
      const mockReports = [
        {
          id: 1,
          year: currentYear,
          quarter: 'Q2',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'direct.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: mockReports })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('direct.zip')).toBeInTheDocument()
      })
    })
  })

  describe('Multiple Reports Display', () => {
    it('displays multiple reports for the same year', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()
      const mockReports = [
        {
          id: 1,
          year: currentYear,
          quarter: 'Q2',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'report1.zip',
        },
        {
          id: 2,
          year: currentYear,
          quarter: 'Q1',
          created_at: '2025-01-08T09:48:00Z',
          original_filename: 'report2.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockReports } })

      renderComponent()

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
      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe('2024')
      })
    })

    it('fetches reports with year from URL parameter', async () => {
      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({
            params: { year: 2024 },
          })
        )
      })
    })

    it('falls back to current fiscal year for invalid year param', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()

      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderWithUrl('/feedback-reports?year=invalid')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe(String(currentYear))
      })
    })

    it('falls back to current fiscal year for out-of-range year', async () => {
      const currentYear =
        new Date().getMonth() > 8
          ? new Date().getFullYear() + 1
          : new Date().getFullYear()

      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderWithUrl('/feedback-reports?year=1999')

      await waitFor(() => {
        const yearSelect = screen.getByLabelText(/Fiscal Year/i)
        expect(yearSelect.value).toBe(String(currentYear))
      })
    })

    it('displays heading with year from URL parameter', async () => {
      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderWithUrl('/feedback-reports?year=2024')

      await waitFor(() => {
        expect(
          screen.getByText('Fiscal Year 2024 Feedback Reports')
        ).toBeInTheDocument()
      })
    })
  })
})
