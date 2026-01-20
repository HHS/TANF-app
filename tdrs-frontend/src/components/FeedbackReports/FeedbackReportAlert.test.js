import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
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

describe('FeedbackReportAlert', () => {
  const renderComponent = () =>
    render(
      <MemoryRouter>
        <FeedbackReportAlert />
      </MemoryRouter>
    )

  beforeEach(() => {
    jest.clearAllMocks()
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
})
