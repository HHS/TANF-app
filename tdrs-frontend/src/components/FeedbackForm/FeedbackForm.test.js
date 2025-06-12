import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackForm from './FeedbackForm'
import { feedbackPost } from '__mocks__/mockFeedbackAxiosApi'
console.log('***FeedbackForm:', FeedbackForm)

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

  it('submits feedback with rating, message, and anonymous flag', async () => {
    feedbackPost.mockResolvedValueOnce({ status: 200 })

    render(<FeedbackForm onFeedbackSubmit={mockOnFeedbackSubmit} />)

    // Simulate selecting a rating
    const ratingInput = screen.getByTestId('feedback-radio-input-4') // "Satisfied"
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
})
