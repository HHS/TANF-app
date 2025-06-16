import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackForm from './FeedbackForm'
import { feedbackPost } from '__mocks__/mockFeedbackAxiosApi'

jest.mock('__mocks__/mockFeedbackAxiosApi', () => ({
  feedbackPost: jest.fn(),
}))

jest.mock('../../assets/feedback/very-dissatisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-very-bad',
        title: 'Very Dissatisfied',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/dissatisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-bad',
        title: 'Dissatisfied',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/neutral-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-fair',
        title: 'Fair',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/satisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-good',
        title: 'Satisfied',
        role: 'svg',
      }),
  }
})

jest.mock('../../assets/feedback/very-satisfied-feedback.svg', () => {
  const React = require('react')
  return {
    ReactComponent: () =>
      React.createElement('svg', {
        'data-testid': 'icon-very-good',
        title: 'Very Satisfied',
        role: 'svg',
      }),
  }
})

describe('Feedback Form tests', () => {
  const mockOnFeedbackSubmit = jest.fn()

  beforeEach(() => {
    feedbackPost.mockClear()
    mockOnFeedbackSubmit.mockClear()
  })

  it('renders feedback form', () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    // Check initial form elements
    expect(screen.getByTestId('fields-required-text')).toHaveTextContent(
      /Fields marked with an asterisk/i
    )
    const ratingRadioGroup = screen.getByTestId('feedback-ratings-select-group')
    expect(ratingRadioGroup).toBeInTheDocument()
    const textarea = screen.getByTestId('feedback-message-input')
    expect(textarea).toBeInTheDocument()
    const submitButton = screen.getByTestId('feedback-submit-button')
    expect(submitButton).toBeInTheDocument()
  })

  it('updates feedback message on user input', () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    const textarea = screen.getByTestId('feedback-message-input')
    fireEvent.change(textarea, { target: { value: 'Test feedback' } })
    expect(textarea.value).toBe('Test feedback')
  })

  it('shows updated character count as user types', () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    const textarea = screen.getByTestId('feedback-message-input')
    fireEvent.change(textarea, { target: { value: 'Hello' } })
    expect(screen.getByText('5/500 characters')).toBeInTheDocument()
  })

  it('trims leading whitespace from feedback input', () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    const textarea = screen.getByTestId('feedback-message-input')
    fireEvent.change(textarea, { target: { value: '   leading space' } })
    expect(textarea.value).toBe('leading space')
  })

  it('toggles anonymous checkbox', () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    const checkbox = screen.getByLabelText(/Send anonymously/i)
    expect(checkbox.checked).toBe(false)
    fireEvent.click(checkbox)
    expect(checkbox.checked).toBe(true)
  })

  it('shows error if rating is not selected on submit', async () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)
    const submitButton = screen.getByTestId('feedback-submit-button')

    // Initially error message should not be present
    expect(screen.queryByText(/There is 1 error in this form/i)).toBeNull()

    fireEvent.click(submitButton)

    // await for error message to appear and styles to update
    await waitFor(() => {
      expect(
        screen.getByText(/There is 1 error in this form/i)
      ).toBeInTheDocument()
    })

    expect(feedbackPost).not.toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ rating: expect.any(Number) })
    )
    expect(mockOnFeedbackSubmit).not.toHaveBeenCalled()
  })

  it('does not proceed if user submits multiple times without selecting rating', async () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    fireEvent.click(screen.getByTestId('feedback-submit-button'))
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() => {
      expect(
        screen.getByText(/There is 1 error in this form/i)
      ).toBeInTheDocument()
    })

    expect(feedbackPost).not.toHaveBeenCalled()
  })

  it('clears error message after rating is selected and form is resubmitted', async () => {
    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() => {
      expect(
        screen.getByText(/There is 1 error in this form/i)
      ).toBeInTheDocument()
    })

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(screen.queryByText(/There is 1 error in this form/i)).toBeNull()
    )
  })

  it('submits feedback with rating, message, and anonymous flag', async () => {
    feedbackPost.mockResolvedValueOnce({ status: 200 })

    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    // Simulate selecting a rating
    const ratingInput = screen.getByTestId('feedback-radio-input-4')
    fireEvent.click(ratingInput)

    // Simulate entering feedback message
    fireEvent.change(screen.getByTestId('feedback-message-input'), {
      target: { value: 'Great!! test feedback' },
    })

    // Simulate checking anonymous
    fireEvent.click(screen.getByLabelText(/Send anonymously/i))

    // Submit
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(feedbackPost).toHaveBeenCalledWith('/api/userFeedback/', {
        rating: 4,
        feedback: 'Great!! test feedback',
        anonymous: true,
      })
    )
    expect(mockOnFeedbackSubmit).toHaveBeenCalled()
  })

  it('submits with rating and no feedback message', async () => {
    feedbackPost.mockResolvedValueOnce({ status: 200 })

    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    fireEvent.click(screen.getByTestId('feedback-radio-input-3'))
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(feedbackPost).toHaveBeenCalledWith('/api/userFeedback/', {
        rating: 3,
        feedback: '',
        anonymous: false,
      })
    )
  })

  it('resets form fields after successful submission', async () => {
    feedbackPost.mockResolvedValueOnce({ status: 200 })

    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))
    fireEvent.change(screen.getByTestId('feedback-message-input'), {
      target: { value: 'Feedback to reset' },
    })
    fireEvent.click(screen.getByLabelText(/Send anonymously/i))

    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() => {
      expect(screen.getByTestId('feedback-message-input').value).toBe('')
      expect(screen.getByLabelText(/Send anonymously/i).checked).toBe(false)
    })
  })

  it('does not reset form on failed feedback submission', async () => {
    feedbackPost.mockResolvedValueOnce({ status: 500 })

    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))
    fireEvent.change(screen.getByTestId('feedback-message-input'), {
      target: { value: 'Should not reset' },
    })

    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(screen.getByTestId('feedback-message-input').value).toBe(
        'Should not reset'
      )
    )
  })

  it('logs error message when API returns 400', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    feedbackPost.mockRejectedValueOnce({
      response: { status: 400 },
    })

    render(<FeedbackForm onFeedbackSubmit={jest.fn()} />)

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error submitting feedback:',
        expect.any(Object)
      )
    )

    consoleSpy.mockRestore()
  })

  it('logs an error if feedbackPost returns non-200 status', async () => {
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation(() => {})
    feedbackPost.mockResolvedValueOnce({ status: 500 })

    render(<FeedbackForm onFeedbackSubmit={jest.fn()} />)

    fireEvent.click(screen.getByTestId('feedback-radio-input-4'))
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith(
        'Something went wrong. Please try again.'
      )
    )

    consoleSpy.mockRestore()
  })

  it('logs fallback error if API throws unexpected error', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    feedbackPost.mockRejectedValueOnce(new Error('Network down'))

    render(<FeedbackForm onFeedbackSubmit={jest.fn()} />)

    fireEvent.click(screen.getByTestId('feedback-radio-input-1'))
    fireEvent.click(screen.getByTestId('feedback-submit-button'))

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith(
        'An unexpected error occurred. Please try again later.'
      )
    )

    consoleSpy.mockRestore()
  })
})
