import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import FeedbackReportAlert from './FeedbackReportAlert'
import axiosInstance from '../../axios-instance'

// Mock the axios instance
jest.mock('../../axios-instance')

// Mock the ReportsContext
const mockUseReportsContext = jest.fn()
jest.mock('../Reports/ReportsContext', () => ({
  useReportsContext: () => mockUseReportsContext(),
}))

// Mock localStorage
const mockLocalStorage = (() => {
  let store = {}
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value
    }),
    clear: jest.fn(() => {
      store = {}
    }),
    removeItem: jest.fn((key) => {
      delete store[key]
    }),
  }
})()

Object.defineProperty(window, 'localStorage', { value: mockLocalStorage })

describe('FeedbackReportAlert', () => {
  const renderComponent = () =>
    render(
      <MemoryRouter>
        <FeedbackReportAlert />
      </MemoryRouter>
    )

  beforeEach(() => {
    jest.clearAllMocks()
    mockLocalStorage.clear()
  })

  it('renders null when yearInputValue is not set', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: null,
      quarterInputValue: 'Q1',
    })

    const { container } = renderComponent()
    expect(container.firstChild).toBeNull()
    expect(axiosInstance.get).not.toHaveBeenCalled()
  })

  it('renders null when quarterInputValue is not set', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: null,
    })

    const { container } = renderComponent()
    expect(container.firstChild).toBeNull()
    expect(axiosInstance.get).not.toHaveBeenCalled()
  })

  it('fetches latest report when year and quarter are set', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [{ created_at: '2025-12-01T00:00:00Z' }],
      },
    })

    renderComponent()

    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/'),
        expect.objectContaining({
          params: {
            year: '2025',
            quarter: 'Q1',
            latest: 'true',
          },
          withCredentials: true,
        })
      )
    })
  })

  it('renders alert when API returns a report', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [{ created_at: '2025-12-01T00:00:00Z' }],
      },
    })

    renderComponent()

    await waitFor(() => {
      expect(screen.getByText(/Feedback Reports Available/)).toBeInTheDocument()
    })
  })

  it('renders null when API returns empty results', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [],
      },
    })

    const { container } = renderComponent()

    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalled()
    })

    expect(container.querySelector('.usa-alert')).toBeNull()
  })

  it('renders null when API call fails', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockRejectedValue(new Error('API error'))

    const { container } = renderComponent()

    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalled()
    })

    expect(container.querySelector('.usa-alert')).toBeNull()
  })

  it('formats date correctly', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [{ created_at: '2025-12-01T00:00:00Z' }],
      },
    })

    renderComponent()

    await waitFor(() => {
      expect(screen.getByText(/12\/1\/2025/)).toBeInTheDocument()
    })
  })

  it('contains link to feedback reports page with year param', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [{ created_at: '2025-12-01T00:00:00Z' }],
      },
    })

    renderComponent()

    await waitFor(() => {
      const link = screen.getByRole('link', { name: /review the feedback/i })
      expect(link).toHaveAttribute('href', '/feedback-reports?year=2025')
    })
  })

  it('has correct USWDS alert classes', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [{ created_at: '2025-12-01T00:00:00Z' }],
      },
    })

    const { container } = renderComponent()

    await waitFor(() => {
      const alert = container.querySelector('.usa-alert')
      expect(alert).toHaveClass('usa-alert--info')
      expect(alert).toHaveClass('margin-top-4')
      expect(alert).toHaveClass('margin-bottom-4')
    })
  })

  it('contains instructional text', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: {
        results: [{ created_at: '2025-12-01T00:00:00Z' }],
      },
    })

    renderComponent()

    await waitFor(() => {
      expect(
        screen.getByText(/resubmit complete and accurate data/i)
      ).toBeInTheDocument()
    })
  })

  it('refetches when year changes', async () => {
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2025',
      quarterInputValue: 'Q1',
    })

    axiosInstance.get.mockResolvedValue({
      data: { results: [{ created_at: '2025-12-01T00:00:00Z' }] },
    })

    const { rerender } = render(
      <MemoryRouter>
        <FeedbackReportAlert />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledTimes(1)
    })

    // Change the year
    mockUseReportsContext.mockReturnValue({
      yearInputValue: '2024',
      quarterInputValue: 'Q1',
    })

    rerender(
      <MemoryRouter>
        <FeedbackReportAlert />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(axiosInstance.get).toHaveBeenCalledTimes(2)
    })
  })

  describe('Dismissable alert functionality', () => {
    it('renders dismiss button with correct aria-label', async () => {
      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: '2025-12-01T00:00:00Z' }],
        },
      })

      renderComponent()

      await waitFor(() => {
        const dismissButton = screen.getByRole('button', {
          name: /dismiss alert/i,
        })
        expect(dismissButton).toBeInTheDocument()
      })
    })

    it('hides alert when dismiss button is clicked', async () => {
      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: '2025-12-01T00:00:00Z' }],
        },
      })

      const { container } = renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Reports Available/)
        ).toBeInTheDocument()
      })

      const dismissButton = screen.getByRole('button', {
        name: /dismiss alert/i,
      })
      fireEvent.click(dismissButton)

      await waitFor(() => {
        expect(container.querySelector('.usa-alert')).toBeNull()
      })
    })

    it('saves dismissed state to localStorage on dismiss', async () => {
      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      const createdAt = '2025-12-01T00:00:00Z'
      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: createdAt }],
        },
      })

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Reports Available/)
        ).toBeInTheDocument()
      })

      const dismissButton = screen.getByRole('button', {
        name: /dismiss alert/i,
      })
      fireEvent.click(dismissButton)

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'feedbackAlertDismissed_2025',
        createdAt
      )
    })

    it('does not render alert when previously dismissed for same report', async () => {
      const createdAt = '2025-12-01T00:00:00Z'

      // Set up localStorage to indicate alert was dismissed for this report
      mockLocalStorage.getItem.mockReturnValue(createdAt)

      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: createdAt }],
        },
      })

      const { container } = renderComponent()

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalled()
      })

      // Alert should not be visible because it was dismissed
      expect(container.querySelector('.usa-alert')).toBeNull()
    })

    it('renders alert again when new report is available (different created_at)', async () => {
      const oldCreatedAt = '2025-12-01T00:00:00Z'
      const newCreatedAt = '2025-12-15T00:00:00Z'

      // Set up localStorage with old dismissed timestamp
      mockLocalStorage.getItem.mockReturnValue(oldCreatedAt)

      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      // API returns a new report with different created_at
      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: newCreatedAt }],
        },
      })

      renderComponent()

      // Alert should be visible because a new report is available
      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Reports Available/)
        ).toBeInTheDocument()
      })
    })

    it('renders alert when fiscal year changes even if previous year was dismissed', async () => {
      // Set up localStorage with dismissed state for 2024
      mockLocalStorage.getItem.mockImplementation((key) => {
        if (key === 'feedbackAlertDismissed_2024') {
          return '2024-12-01T00:00:00Z'
        }
        return null
      })

      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: '2025-12-01T00:00:00Z' }],
        },
      })

      renderComponent()

      // Alert should be visible for 2025 even though 2024 was dismissed
      await waitFor(() => {
        expect(
          screen.getByText(/Feedback Reports Available/)
        ).toBeInTheDocument()
      })
    })

    it('dismiss button has correct styling', async () => {
      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: '2025-12-01T00:00:00Z' }],
        },
      })

      renderComponent()

      await waitFor(() => {
        const dismissButton = screen.getByRole('button', {
          name: /dismiss alert/i,
        })
        expect(dismissButton).toHaveClass('usa-modal__close')
        expect(dismissButton).toHaveClass('feedback-modal-close-button')
      })
    })

    it('alert body has flex layout for dismiss button positioning', async () => {
      mockUseReportsContext.mockReturnValue({
        yearInputValue: '2025',
        quarterInputValue: 'Q1',
      })

      axiosInstance.get.mockResolvedValue({
        data: {
          results: [{ created_at: '2025-12-01T00:00:00Z' }],
        },
      })

      const { container } = renderComponent()

      await waitFor(() => {
        const alertBody = container.querySelector('.usa-alert__body')
        expect(alertBody).toHaveStyle({ display: 'flex' })
        expect(alertBody).toHaveStyle({ justifyContent: 'space-between' })
        expect(alertBody).toHaveStyle({ alignItems: 'center' })
      })
    })
  })
})
