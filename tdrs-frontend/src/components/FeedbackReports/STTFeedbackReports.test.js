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

    it('renders the search button', async () => {
      renderComponent()

      await waitFor(() => {
        const searchButton = screen.getByRole('button', { name: /Search/i })
        expect(searchButton).toBeInTheDocument()
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
    it('fetches reports on mount', async () => {
      renderComponent()

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/'),
          expect.objectContaining({ withCredentials: true })
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
    it('does not filter reports until Search is clicked', async () => {
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
          original_filename: 'FYCurrent.zip',
        },
        {
          id: 2,
          year: 2024,
          quarter: 'Q4',
          created_at: '2024-11-08T09:48:00Z',
          original_filename: 'FY2024.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockReports } })

      renderComponent()

      // Wait for initial load - should show current year's reports
      await waitFor(() => {
        expect(screen.getByText('FYCurrent.zip')).toBeInTheDocument()
      })

      // Change to 2024 - should NOT immediately change the displayed reports
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2024' } })

      // Reports should still show current year (not yet searched)
      expect(screen.getByText('FYCurrent.zip')).toBeInTheDocument()
      expect(screen.queryByText('FY2024.zip')).not.toBeInTheDocument()
    })

    it('filters reports by selected year when Search is clicked', async () => {
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
          original_filename: 'FYCurrent.zip',
        },
        {
          id: 2,
          year: 2024,
          quarter: 'Q4',
          created_at: '2024-11-08T09:48:00Z',
          original_filename: 'FY2024.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockReports } })

      renderComponent()

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('FYCurrent.zip')).toBeInTheDocument()
      })

      // Change to 2024
      const yearSelect = screen.getByLabelText(/Fiscal Year/i)
      fireEvent.change(yearSelect, { target: { value: '2024' } })

      // Click Search button
      const searchButton = screen.getByRole('button', { name: /Search/i })
      fireEvent.click(searchButton)

      // Now reports should be filtered to 2024
      await waitFor(() => {
        expect(screen.getByText('FY2024.zip')).toBeInTheDocument()
        expect(screen.queryByText('FYCurrent.zip')).not.toBeInTheDocument()
      })
    })
  })

  describe('Search Button', () => {
    it('refetches reports when search is clicked', async () => {
      renderComponent()

      // Wait for initial fetch to complete
      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledTimes(1)
      })

      // Wait for loading to finish so button is enabled
      const searchButton = screen.getByRole('button', { name: /Search/i })
      await waitFor(() => {
        expect(searchButton.disabled).toBe(false)
      })

      fireEvent.click(searchButton)

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledTimes(2)
      })
    })

    it('is disabled while loading', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      renderComponent()

      const searchButton = screen.getByRole('button', { name: /Search/i })
      expect(searchButton).toHaveAttribute('disabled')
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
})
