import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import FeedbackWidget from './FeedbackWidget'

jest.useFakeTimers()

// jest.mock('./FeedbackForm', () => (props) => (
//   <div data-testid="mock-feedback-form">
//     <button onClick={() => props.onFeedbackSubmit()}>Submit</button>
//   </div>
// ))

jest.mock('./FeedbackForm', () => (props) => (
  <div data-testid="mock-feedback-form">
    <button
      onClick={() => {
        props.onFeedbackSubmit()
        props.onRequestSuccess?.()
      }}
    >
      Submit
    </button>
  </div>
))

describe('FeedbackWidget', () => {
  const defaultProps = {
    isOpen: true,
    onClose: jest.fn(),
  }

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('does not render when isOpen is false', () => {
    const { container } = render(
      <FeedbackWidget {...defaultProps} isOpen={false} />
    )
    expect(container.firstChild).toBeNull()
  })

  it('renders with TANF header', () => {
    render(<FeedbackWidget {...defaultProps} dataType="tanf" />)
    expect(screen.getByText(/TANF/i)).toBeInTheDocument()
  })

  it('renders with SSP-MOE header', () => {
    render(<FeedbackWidget {...defaultProps} dataType="ssp-moe" />)
    expect(screen.getByText(/SSP-MOE/i)).toBeInTheDocument()
  })

  it('renders with FRA header by default', () => {
    render(<FeedbackWidget {...defaultProps} />)
    expect(screen.getByText(/FRA/i)).toBeInTheDocument()
  })

  it('exposes internal ref via forwardRef', () => {
    const testRef = React.createRef()
    render(<FeedbackWidget {...defaultProps} ref={testRef} />)
    expect(testRef.current).toBeInstanceOf(HTMLElement)
  })

  it('calls onClose when close button is clicked', () => {
    render(<FeedbackWidget {...defaultProps} />)
    const closeButton = screen.getByTestId('feedback-widget-close-button')
    fireEvent.click(closeButton)
    expect(defaultProps.onClose).toHaveBeenCalled()
  })

  it('closes when Escape key is pressed', () => {
    render(<FeedbackWidget {...defaultProps} />)
    const widget = screen.getByRole('dialog')
    fireEvent.keyDown(widget, { key: 'Escape', code: 'Escape' })
    expect(defaultProps.onClose).toHaveBeenCalled()
  })

  it('submits feedback and shows thank you message and spinner', async () => {
    render(<FeedbackWidget {...defaultProps} />)

    // Submit feedback
    const submitButton = screen.getByText('Submit')
    fireEvent.click(submitButton)

    // Thank you message appears
    expect(
      await screen.findByText(/Thank you for your feedback!/i)
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Loading')).toBeInTheDocument()

    // Fast-forward timers
    jest.advanceTimersByTime(1000)

    await waitFor(() => {
      expect(defaultProps.onClose).toHaveBeenCalled()
    })
  })

  it('does not show spinner initially', () => {
    render(<FeedbackWidget {...defaultProps} />)
    expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
  })

  it('removes spinner after timeout', async () => {
    render(<FeedbackWidget {...defaultProps} />)
    fireEvent.click(screen.getByText('Submit'))

    expect(screen.getByLabelText('Loading')).toBeInTheDocument()

    jest.advanceTimersByTime(1000)

    await waitFor(() => {
      expect(screen.queryByLabelText('Loading')).not.toBeInTheDocument()
    })
  })
})
