import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackForm from './FeedbackForm'

describe('Feedback Form tests', () => {
  const setup = () => render(<FeedbackForm onFeedbackSubmit={jest.fn()} />)

  it('renders feedback form', () => {
    setup()

    // Check initial form elements
    const ratingRadioGroup = screen.getByTestId('feedback-ratings-select-group')
    expect(ratingRadioGroup).toBeInTheDocument()
    const textarea = screen.getByTestId('feedback-textarea')
    expect(textarea).toBeInTheDocument()
    const submitButton = screen.getByTestId('feedback-submit-button')
    expect(submitButton).toBeInTheDocument()
  })

  it('handles empty (invalid) feedback submission attempt', () => {
    setup()

    const fieldsRequiredText = screen.getByTestId('fields-required-text')
    const ratingRadioGroup = screen.getByTestId('feedback-ratings-select-group')
    const textarea = screen.getByTestId('feedback-textarea')
    const submitButton = screen.getByTestId('feedback-submit-button')
    // Check error message not showing
    expect(
      screen.getByText('There is 1 error in this form')
    ).not.toBeInTheDocument()

    // Simulate empty submission
    // No rating selected
    fireEvent.change(textarea, { target: { value: '' } })
    fireEvent.click(submitButton)

    // Expect error colors to take effect and error message to be displayed
    expect(fieldsRequiredText).toHaveStyle('color: red')
    expect(ratingRadioGroup).toHaveStyle('outline: 2px solid #b50909')
    expect(
      screen.getByText('There is 1 error in this form')
    ).toBeInTheDocument()
  })

  //   it('handles rating selection amd feedback message (valid) submission', () => {
  //     const fieldsRequiredText = screen.getByTestId('fields-required-text')
  //     const ratingRadioGroup = screen.getByTestId('feedback-rating-select-group')
  //     const textarea = screen.getByTestId('feedback-textarea')
  //     const submitButton = screen.getByTestId('feedback-submit-button')
  //     // Check error message not showing
  //     expect(
  //       screen.getByText('There is 1 error in this form')
  //     ).not.toBeInTheDocument()

  //     // Simulate selecting a rating and typing feedback

  //     fireEvent.change(textarea, { target: { value: 'Great app!' } })
  //     fireEvent.click(submitButton)

  //     // Check for success message
  //     expect(screen.getByText('Thank you for your feedback')).toBeInTheDocument()
  //   })
})
