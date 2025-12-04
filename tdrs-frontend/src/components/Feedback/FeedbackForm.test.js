import React from 'react'
import * as reactRedux from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackForm from './FeedbackForm'
import { useSelector } from 'react-redux'
import axiosInstance from '../../axios-instance'

// Mock the Redux selector
jest.mock('react-redux', () => ({
  ...jest.requireActual('react-redux'),
  useSelector: jest.fn(),
}))

jest.mock('../../axios-instance')

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
    axiosInstance.post.mockClear()
    axiosInstance.patch.mockClear()
    mockOnFeedbackSubmit.mockClear()
    // Default to authenticated for most tests
    reactRedux.useSelector.mockImplementation(() => true)
  })

  it('renders feedback form', () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    // Check initial form elements
    expect(screen.getByTestId('fields-required-text')).toHaveTextContent(
      /Fields marked with an asterisk/i
    )
    const ratingRadioGroup = screen.getByTestId('feedback-ratings-select-group')
    expect(ratingRadioGroup).toBeInTheDocument()
    const textarea = screen.getByTestId('feedback-message-input')
    expect(textarea).toBeInTheDocument()
    const submitButton = screen.getByRole('button', { name: /send feedback/i })
    expect(submitButton).toBeInTheDocument()
  })

  it('updates feedback message and caharcter count on user input', () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    const textarea = screen.getByTestId('feedback-message-input')
    fireEvent.change(textarea, { target: { value: 'Hello' } })
    expect(textarea.value).toBe('Hello')
    expect(screen.getByText('5/500 characters')).toBeInTheDocument()
  })

  it('trims leading whitespace from feedback input', () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    const textarea = screen.getByTestId('feedback-message-input')
    fireEvent.change(textarea, { target: { value: '   leading space' } })
    expect(textarea.value).toBe('leading space')
  })

  it('toggles anonymous checkbox with mouse click', () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    const checkbox = screen.getByLabelText(/Send anonymously/i)
    expect(checkbox.checked).toBe(false)
    fireEvent.click(checkbox)
    expect(checkbox.checked).toBe(true)
  })

  it('toggles anonymous checkbox with Enter key', () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    const checkbox = screen.getByLabelText(/Send anonymously/i)
    checkbox.focus()
    fireEvent.keyDown(checkbox, { key: 'Enter', code: 'Enter' })

    expect(checkbox.checked).toBe(true)
  })

  it('does not show anonymous checkbox when user is not authenticated', () => {
    // Override useSelector to simulate unauthenticated user
    reactRedux.useSelector.mockImplementation(() => false)

    render(
      <FeedbackForm isGeneralFeedback={true} onFeedbackSubmit={jest.fn()} />
    )

    // Check that checkbox is NOT in the document
    expect(screen.queryByLabelText(/Send anonymously/i)).toBeNull()

    // Restore useSelector to default (authenticated: true) for other tests
    useSelector.mockImplementation(() => true)
  })

  it('shows error if rating is not selected on submit', async () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )
    const submitButton = screen.getByRole('button', { name: /send feedback/i })

    // Initially error message should not be present
    expect(screen.queryByText(/There is 1 error in this form/i)).toBeNull()

    fireEvent.click(submitButton)

    // await for error message to appear and styles to update
    await waitFor(() => {
      expect(
        screen.getByText(/There is 1 error in this form/i)
      ).toBeInTheDocument()
    })

    expect(axiosInstance.post).not.toHaveBeenCalledWith(
      expect.anything(),
      expect.objectContaining({ rating: expect.any(Number) })
    )
    expect(mockOnFeedbackSubmit).not.toHaveBeenCalled()
  })

  it('does not proceed if user submits multiple times without selecting rating', async () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/There is 1 error in this form/i)
      ).toBeInTheDocument()
    })

    expect(axiosInstance.post).not.toHaveBeenCalled()
  })

  it('clears error message after rating is selected', async () => {
    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() => {
      expect(
        screen.getByText(/There is 1 error in this form/i)
      ).toBeInTheDocument()
    })

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))

    await waitFor(() =>
      expect(screen.queryByText(/There is 1 error in this form/i)).toBeNull()
    )
  })

  it('submits feedback with rating, message, and anonymous flag', async () => {
    axiosInstance.post.mockResolvedValue({ status: 201, data: { id: 1 } })
    axiosInstance.patch.mockResolvedValue({ status: 200, data: { id: 1 } })

    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

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
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith(
        expect.stringContaining('/feedback/'),
        {
          rating: 4,
          component: 'general-website',
          feedback: 'Great!! test feedback',
          feedback_type: 'general_feedback',
          page_url: 'http://localhost/',
          anonymous: true,
        },
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      )
    })
    expect(mockOnFeedbackSubmit).toHaveBeenCalled()
  })

  it('submits with rating and no feedback message', async () => {
    axiosInstance.post.mockResolvedValue({ status: 201, data: { id: 1 } })
    axiosInstance.patch.mockResolvedValue({ status: 200, data: { id: 1 } })

    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    fireEvent.click(screen.getByTestId('feedback-radio-input-3'))
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() =>
      expect(axiosInstance.post).toHaveBeenCalledWith(
        expect.stringContaining('/feedback/'),
        {
          component: 'general-website',
          feedback_type: 'general_feedback',
          page_url: 'http://localhost/',
          rating: 3,
          feedback: '',
          anonymous: false,
        },
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      )
    )
  })

  it('submits form using Enter key on submit button', async () => {
    axiosInstance.post.mockResolvedValue({ status: 201, data: { id: 1 } })
    axiosInstance.patch.mockResolvedValue({ status: 200, data: { id: 1 } })

    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    fireEvent.click(screen.getByTestId('feedback-radio-input-3'))

    const button = screen.getByTestId('feedback-submit-button')
    // Focus the button and simulate Enter keypress
    button.focus()
    fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' })

    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalled()
      expect(mockOnFeedbackSubmit).toHaveBeenCalled()
    })
  })

  it('submits form with Cmd/Ctrl + Enter from inside textarea', async () => {
    axiosInstance.post.mockResolvedValue({ status: 201, data: { id: 1 } })
    axiosInstance.patch.mockResolvedValue({ status: 200, data: { id: 1 } })

    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    const textarea = screen.getByTestId('feedback-message-input')
    textarea.focus()
    fireEvent.change(textarea, { target: { value: 'Quick feedback' } })
    fireEvent.click(screen.getByTestId('feedback-radio-input-3'))

    fireEvent.keyDown(window, { key: 'Enter', metaKey: true }) // Mac
    // OR use ctrlKey: true for Windows

    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalled()
      expect(mockOnFeedbackSubmit).toHaveBeenCalled()
    })
  })

  it('resets form fields after successful submission', async () => {
    axiosInstance.post.mockResolvedValue({ status: 201, data: { id: 1 } })
    axiosInstance.patch.mockResolvedValue({ status: 200, data: { id: 1 } })

    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    const rating = screen.getByTestId('feedback-radio-input-2')
    fireEvent.click(rating)
    fireEvent.change(screen.getByTestId('feedback-message-input'), {
      target: { value: 'Feedback to reset' },
    })
    fireEvent.click(screen.getByLabelText(/Send anonymously/i))

    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() => {
      expect(screen.getByTestId('feedback-radio-input-2').checked).toBe(false)
      expect(screen.getByTestId('feedback-message-input').value).toBe('')
      expect(screen.getByLabelText(/Send anonymously/i).checked).toBe(false)
    })
  })

  it('does not reset form on failed feedback submission', async () => {
    axiosInstance.post.mockResolvedValueOnce({ status: 500 })

    render(
      <FeedbackForm
        isGeneralFeedback={true}
        onFeedbackSubmit={mockOnFeedbackSubmit}
      />
    )

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))
    fireEvent.change(screen.getByTestId('feedback-message-input'), {
      target: { value: 'Should not reset' },
    })

    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() =>
      expect(screen.getByTestId('feedback-message-input').value).toBe(
        'Should not reset'
      )
    )
  })

  it('logs error message when API returns 400', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    axiosInstance.post.mockRejectedValueOnce({
      response: { status: 400 },
    })

    render(
      <FeedbackForm isGeneralFeedback={true} onFeedbackSubmit={jest.fn()} />
    )

    fireEvent.click(screen.getByTestId('feedback-radio-input-2'))
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error submitting feedback:',
        expect.any(Object)
      )
    )
    consoleSpy.mockRestore()
  })

  it('logs an error if feedbackPost returns non-200 status', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    axiosInstance.post.mockResolvedValueOnce({ status: 500 })

    render(
      <FeedbackForm isGeneralFeedback={true} onFeedbackSubmit={jest.fn()} />
    )

    fireEvent.click(screen.getByTestId('feedback-radio-input-4'))
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith(
        'Error submitting feedback:',
        expect.any(Object)
      )
    )
    consoleSpy.mockRestore()
  })

  it('logs fallback error if API throws unexpected error', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {})
    axiosInstance.post.mockRejectedValueOnce(new Error('Network down'))

    render(
      <FeedbackForm isGeneralFeedback={true} onFeedbackSubmit={jest.fn()} />
    )

    fireEvent.click(screen.getByTestId('feedback-radio-input-1'))
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() =>
      expect(consoleSpy).toHaveBeenCalledWith(
        'An unexpected error occurred. Please try again later.',
        expect.any(Object)
      )
    )
    consoleSpy.mockRestore()
  })

  it('renders correctly when isGeneralFeedback is false (e.g., in modal)', () => {
    render(
      <FeedbackForm isGeneralFeedback={false} onFeedbackSubmit={jest.fn()} />
    )

    // Optional hint should be visible (if it's specific feedback)
    expect(
      screen.getByText(/Pick a score and leave a comment/i)
    ).toBeInTheDocument()

    // Character counter should NOT be visible (assumes it's only in general feedback)
    expect(screen.queryByText(/\/500 characters/i)).toBeNull()

    // Anonymous checkbox may be hidden in specific feedback
    expect(screen.queryByLabelText(/Send anonymously/i)).toBeInTheDocument()

    // Ensure rating group renders with appropriate role/label
    expect(
      screen.getByTestId('feedback-ratings-select-group')
    ).toBeInTheDocument()
  })

  it('submits minimal fields when isGeneralFeedback is false', async () => {
    axiosInstance.post.mockResolvedValue({ status: 201, data: { id: 1 } })
    axiosInstance.patch.mockResolvedValue({ status: 200, data: { id: 1 } })

    render(
      <FeedbackForm
        isGeneralFeedback={false}
        onFeedbackSubmit={mockOnFeedbackSubmit}
        dataType="fra_submission_feedback"
      />
    )

    // Provide required rating
    fireEvent.click(screen.getByTestId('feedback-radio-input-5'))

    // Skip comment input (allowed)
    fireEvent.click(screen.getByRole('button', { name: /send feedback/i }))

    await waitFor(() => {
      expect(axiosInstance.post).toHaveBeenCalledWith(
        expect.any(String),
        {
          attachments: [],
          component: 'data-file-submission',
          feedback_type: 'fra_submission_feedback',
          page_url: 'http://localhost/',
          widget_id: 'unknown-submission-feedback',
          rating: 5,
          feedback: '', // comment left blank
          anonymous: false, // anonymous checkbox hidden
        },
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      )
      expect(mockOnFeedbackSubmit).toHaveBeenCalled()
    })
  })
})
