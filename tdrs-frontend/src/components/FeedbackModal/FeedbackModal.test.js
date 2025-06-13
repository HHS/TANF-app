import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import '@testing-library/jest-dom'
import FeedbackModal from './FeedbackModal'

describe('FeedbackModal', () => {
  const props = {
    id: 'test-modal',
    title: 'Test Modal Title',
    message: 'This is a test message.',
    isOpen: true,
    onClose: jest.fn(),
    children: <div data-testid="custom-child">Child content</div>,
  }

  beforeEach(() => {
    props.onClose.mockClear()
  })

  it('renders when isOpen is true', () => {
    render(<FeedbackModal {...props} />)

    expect(screen.getByTestId('feedback-modal-header')).toHaveTextContent(
      'Test Modal Title'
    )
    expect(screen.getByText('This is a test message.')).toBeInTheDocument()
    expect(screen.getByTestId('custom-child')).toBeInTheDocument()
  })

  it('does not render when isOpen is false', () => {
    render(<FeedbackModal {...props} isOpen={false} />)

    expect(
      screen.queryByTestId('feedback-modal-header')
    ).not.toBeInTheDocument()
  })

  it('calls onClose when close button is clicked', () => {
    render(<FeedbackModal {...props} />)

    const closeButton = screen.getByRole('button', { name: /close modal/i })
    fireEvent.click(closeButton)

    expect(props.onClose).toHaveBeenCalledTimes(1)
  })

  it('sets focus to header when modal opens', () => {
    render(<FeedbackModal {...props} />)

    const header = screen.getByTestId('feedback-modal-header')
    expect(document.activeElement).toBe(header)
  })

  test('includes proper accessibility attributes', () => {
    render(<FeedbackModal {...props} />)

    const header = screen.getByTestId('feedback-modal-header')
    expect(header).toHaveAttribute('tabIndex', '-1')
    expect(header).toHaveAttribute('aria-describedby', 'modalDescription')
    expect(screen.getByText('This is a test message.')).toHaveAttribute(
      'id',
      'modalDescription'
    )
  })
})
