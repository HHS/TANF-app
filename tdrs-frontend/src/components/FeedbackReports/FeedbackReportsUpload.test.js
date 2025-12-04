import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import FeedbackReportsUpload from './FeedbackReportsUpload'

// Mock Button component
jest.mock('../Button', () => ({
  __esModule: true,
  default: ({ children, onClick, disabled, className, type }) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={className}
      type={type}
      data-testid="mock-button"
    >
      {children}
    </button>
  ),
}))

describe('FeedbackReportsUpload', () => {
  const mockOnFileChange = jest.fn()
  const mockOnUpload = jest.fn()
  const mockInputRef = { current: null }

  const defaultProps = {
    selectedFile: null,
    fileError: null,
    loading: false,
    onFileChange: mockOnFileChange,
    onUpload: mockOnUpload,
    inputRef: mockInputRef,
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  const renderComponent = (props = {}) => {
    return render(<FeedbackReportsUpload {...defaultProps} {...props} />)
  }

  describe('Rendering', () => {
    it('renders label with correct text', () => {
      renderComponent()

      expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
    })

    it('renders file input with correct attributes', () => {
      renderComponent()

      const fileInput = screen.getByLabelText('Feedback Reports ZIP')
      expect(fileInput).toHaveAttribute('type', 'file')
      expect(fileInput).toHaveAttribute('name', 'feedback-reports')
      expect(fileInput).toHaveAttribute('id', 'feedback_reports')
      expect(fileInput).toHaveAttribute(
        'aria-describedby',
        'feedback_reports-file'
      )
      expect(fileInput).toHaveAttribute(
        'data-errormessage',
        'File must be a .zip file'
      )
    })

    it('renders button with correct text', () => {
      renderComponent()

      expect(screen.getByText('Upload & Notify States')).toBeInTheDocument()
    })

    it('applies error class when fileError is set', () => {
      const { container } = renderComponent({ fileError: 'Some error' })

      const formGroup = container.querySelector('.usa-form-group')
      expect(formGroup).toHaveClass('usa-form-group--error')
    })

    it('does not apply error class when fileError is null', () => {
      const { container } = renderComponent({ fileError: null })

      const formGroup = container.querySelector('.usa-form-group')
      expect(formGroup).toHaveClass('usa-form-group')
      expect(formGroup).not.toHaveClass('usa-form-group--error')
    })
  })

  describe('Error Display', () => {
    it('shows error message when fileError prop is set', () => {
      const errorMessage = 'File must be a .zip file'
      renderComponent({ fileError: errorMessage })

      const errorElement = screen.getByText(errorMessage)
      expect(errorElement).toBeInTheDocument()
      expect(errorElement).toHaveClass('usa-error-message')
      expect(errorElement).toHaveAttribute('role', 'alert')
      expect(errorElement).toHaveAttribute('id', 'feedback_reports-error-alert')
    })

    it('does not show error message when fileError is null', () => {
      renderComponent({ fileError: null })

      expect(
        screen.queryByRole('alert', { hidden: false })
      ).not.toBeInTheDocument()
    })
  })

  describe('Aria Description', () => {
    it('shows default aria description when no file selected', () => {
      const { container } = renderComponent({ selectedFile: null })

      const ariaDesc = container.querySelector('#feedback_reports-file')
      expect(ariaDesc).toHaveTextContent(
        'Drag file here or choose from folder.'
      )
    })

    it('shows selected file aria description when file is selected', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      const { container } = renderComponent({ selectedFile: mockFile })

      const ariaDesc = container.querySelector('#feedback_reports-file')
      expect(ariaDesc).toHaveTextContent(
        'Selected File test.zip. To change the selected file, click this button.'
      )
    })
  })

  describe('Button States', () => {
    it('button is disabled when selectedFile is null', () => {
      renderComponent({ selectedFile: null, loading: false })

      const button = screen.getByTestId('mock-button')
      expect(button).toHaveAttribute('disabled')
    })

    it('button is disabled when loading is true', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      renderComponent({ selectedFile: mockFile, loading: true })

      const button = screen.getByTestId('mock-button')
      expect(button).toHaveAttribute('disabled')
    })

    it('button is enabled when file selected and not loading', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      renderComponent({ selectedFile: mockFile, loading: false })

      const button = screen.getByTestId('mock-button')
      expect(button).not.toHaveAttribute('disabled')
    })

    it('button text changes to "Uploading..." when loading', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      renderComponent({ selectedFile: mockFile, loading: true })

      expect(screen.getByText('Uploading...')).toBeInTheDocument()
    })

    it('button shows "Upload & Notify States" when not loading', () => {
      renderComponent({ loading: false })

      expect(screen.getByText('Upload & Notify States')).toBeInTheDocument()
    })
  })

  describe('Interactions', () => {
    it('calls onFileChange when file input changes', () => {
      renderComponent()

      const fileInput = screen.getByLabelText('Feedback Reports ZIP')
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [mockFile] } })

      expect(mockOnFileChange).toHaveBeenCalledTimes(1)
      expect(mockOnFileChange).toHaveBeenCalledWith(
        expect.objectContaining({
          target: expect.objectContaining({
            files: [mockFile],
          }),
        })
      )
    })

    it('calls onUpload when button clicked', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      renderComponent({ selectedFile: mockFile, loading: false })

      const button = screen.getByText('Upload & Notify States')
      fireEvent.click(button)

      expect(mockOnUpload).toHaveBeenCalledTimes(1)
    })

    it('does not call onUpload when button is disabled', () => {
      renderComponent({ selectedFile: null, loading: false })

      const button = screen.getByTestId('mock-button')
      // Even if we try to click, the disabled state should prevent the call
      fireEvent.click(button)

      expect(mockOnUpload).not.toHaveBeenCalled()
    })
  })

  describe('InputRef', () => {
    it('passes inputRef to file input element', () => {
      const testRef = React.createRef()
      renderComponent({ inputRef: testRef })

      const fileInput = screen.getByLabelText('Feedback Reports ZIP')
      expect(testRef.current).toBe(fileInput)
    })
  })
})
