import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import Feedback from './Feedback'

// Mock FeedbackForm with simplified submit button
jest.mock('./FeedbackForm', () => ({ onFeedbackSubmit }) => (
  <div>
    <p>Mock Feedback Form</p>
    <button data-testid="submit-feedback" onClick={onFeedbackSubmit}>
      Send Feedback
    </button>
  </div>
))

describe('Feedback component', () => {
  it('feedback sticky button is always visible initially', () => {
    render(<Feedback />)
    const button = screen.getByRole('button', { name: /give feedback/i })
    expect(button).toBeVisible()
  })

  it('opens modal on button click', () => {
    render(<Feedback />)
    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))
    expect(
      screen.getByRole('heading', { name: /tell us how we can improve/i })
    ).toBeInTheDocument()
    expect(screen.getByText(/mock feedback form/i)).toBeInTheDocument()
    expect(screen.getByTestId('submit-feedback')).toBeInTheDocument()
  })

  it('closes modal on Escape key press', async () => {
    render(<Feedback />)

    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))

    const overlay = screen.getByTestId('feedback-modal-overlay')
    overlay.focus()

    fireEvent.keyDown(overlay, {
      key: 'Escape',
      code: 'Escape',
      bubbles: true,
      cancelable: true,
    })

    // Modal should closed
    await waitFor(() => {
      expect(
        screen.queryByRole('heading', {
          name: /tell us how we can improve/i,
        })
      ).not.toBeInTheDocument()
    })
  })

  it('does not close modal when clicking on the overlay', () => {
    render(<Feedback />)

    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))

    const overlay = screen.getByTestId('feedback-modal-overlay')
    fireEvent.click(overlay)

    expect(
      screen.getByRole('heading', { name: /tell us how we can improve/i })
    ).toBeInTheDocument()
  })

  it('transitions to thank you modal after submitting feedback', async () => {
    render(<Feedback />)

    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))

    fireEvent.click(await screen.findByTestId('submit-feedback'))

    await waitFor(() => {
      expect(
        screen.getByRole('heading', { name: /thank you for your feedback/i })
      ).toBeInTheDocument()
    })

    expect(
      screen.getByText(/your response has been recorded/i)
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /tanfdata@acf.hhs.gov/i })
    ).toBeInTheDocument()

    expect(
      screen.getByTestId('feedback-submit-close-button')
    ).toBeInTheDocument()
  })

  it('closes modal when Close button clicked in thank you modal', async () => {
    render(<Feedback />)

    // Open and submit feedback
    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))
    fireEvent.click(await screen.findByTestId('submit-feedback'))

    await waitFor(() =>
      expect(
        screen.getByRole('heading', { name: /thank you for your feedback/i })
      ).toBeInTheDocument()
    )

    fireEvent.click(screen.getByTestId('modal-close-button'))

    await waitFor(() =>
      expect(
        screen.queryByRole('heading', { name: /thank you for your feedback/i })
      ).not.toBeInTheDocument()
    )

    expect(
      screen.queryByTestId('feedback-modal-overlay')
    ).not.toBeInTheDocument()
  })

  it('closes modal when Enter is pressed on Thank You Modal Close button', async () => {
    render(<Feedback />)

    // Open and submit
    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))
    fireEvent.click(await screen.findByTestId('submit-feedback'))

    await waitFor(() =>
      expect(
        screen.getByRole('heading', { name: /thank you for your feedback/i })
      ).toBeInTheDocument()
    )

    const closeButton = screen.getByTestId('feedback-submit-close-button')
    closeButton.focus()
    fireEvent.keyDown(closeButton, { key: 'Enter', code: 'Enter' })

    await waitFor(() =>
      expect(
        screen.queryByRole('heading', { name: /thank you for your feedback/i })
      ).not.toBeInTheDocument()
    )
  })

  it('resets to feedback form after submitting then reopening', async () => {
    render(<Feedback />)

    // Open and submit
    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))
    fireEvent.click(await screen.findByTestId('submit-feedback'))

    // Wait for thank you modal
    await waitFor(() =>
      expect(
        screen.getByRole('heading', { name: /thank you for your feedback/i })
      ).toBeInTheDocument()
    )

    // Close modal
    fireEvent.click(screen.getByTestId('modal-close-button'))

    // Reopen
    fireEvent.click(screen.getByRole('button', { name: /give feedback/i }))

    expect(
      screen.getByRole('heading', { name: /tell us how we can improve/i })
    ).toBeInTheDocument()
    expect(screen.getByText(/mock feedback form/i)).toBeInTheDocument()
  })

  it('does not render multiple modals when button is clicked multiple times', () => {
    render(<Feedback />)

    const button = screen.getByRole('button', { name: /give feedback/i })
    fireEvent.click(button)
    fireEvent.click(button)

    // Still only one modal
    expect(
      screen.getAllByRole('heading', {
        name: /tell us how we can improve/i,
      }).length
    ).toBe(1)
  })
})
