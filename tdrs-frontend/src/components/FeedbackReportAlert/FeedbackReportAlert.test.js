import React from 'react'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import FeedbackReportAlert from './FeedbackReportAlert'

describe('FeedbackReportAlert', () => {
  const renderWithRouter = (component) =>
    render(<MemoryRouter>{component}</MemoryRouter>)

  it('renders null when latestReportDate is null', () => {
    const { container } = renderWithRouter(
      <FeedbackReportAlert latestReportDate={null} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders null when latestReportDate is undefined', () => {
    const { container } = renderWithRouter(<FeedbackReportAlert />)
    expect(container.firstChild).toBeNull()
  })

  it('renders alert when latestReportDate is provided', () => {
    renderWithRouter(
      <FeedbackReportAlert latestReportDate="2025-12-01T00:00:00Z" />
    )

    expect(screen.getByText(/Feedback Reports Available/)).toBeInTheDocument()
  })

  it('formats date correctly', () => {
    renderWithRouter(
      <FeedbackReportAlert latestReportDate="2025-12-01T00:00:00Z" />
    )

    expect(screen.getByText(/12\/1\/2025/)).toBeInTheDocument()
  })

  it('contains link to feedback reports page', () => {
    renderWithRouter(
      <FeedbackReportAlert latestReportDate="2025-12-01T00:00:00Z" />
    )

    const link = screen.getByRole('link', { name: /review the feedback/i })
    expect(link).toHaveAttribute('href', '/feedback-reports')
  })

  it('has correct USWDS alert classes', () => {
    const { container } = renderWithRouter(
      <FeedbackReportAlert latestReportDate="2025-12-01T00:00:00Z" />
    )

    const alert = container.querySelector('.usa-alert')
    expect(alert).toHaveClass('usa-alert--info')
    expect(alert).toHaveClass('margin-top-4')
    expect(alert).toHaveClass('margin-bottom-4')
  })

  it('contains instructional text', () => {
    renderWithRouter(
      <FeedbackReportAlert latestReportDate="2025-12-01T00:00:00Z" />
    )

    expect(
      screen.getByText(/resubmit complete and accurate data/i)
    ).toBeInTheDocument()
  })
})
