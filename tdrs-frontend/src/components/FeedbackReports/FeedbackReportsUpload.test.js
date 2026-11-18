import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import FeedbackReportsUpload, { formatTypedDate } from './FeedbackReportsUpload'

// Mock USWDS file input
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
  datePicker: {
    init: jest.fn(),
  },
}))

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

  const mockOnDateChange = jest.fn()
  const mockOnDateBlur = jest.fn()

  const defaultProps = {
    selectedFile: null,
    fileError: null,
    loading: false,
    onFileChange: mockOnFileChange,
    onUpload: mockOnUpload,
    inputRef: mockInputRef,
    dateExtractedOn: '',
    dateError: null,
    onDateChange: mockOnDateChange,
    onDateBlur: mockOnDateBlur,
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
        'Invalid file. Make sure to select a zip file.'
      )
    })

    it('renders button with correct text', () => {
      renderComponent()

      expect(screen.getByText('Upload & Notify STTs')).toBeInTheDocument()
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
    it('button is enabled when not loading (validation happens on click)', () => {
      renderComponent({ selectedFile: null, loading: false })

      const button = screen.getByTestId('mock-button')
      expect(button).not.toHaveAttribute('disabled')
    })

    it('button is disabled when loading is true', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      renderComponent({ selectedFile: mockFile, loading: true })

      const button = screen.getByTestId('mock-button')
      expect(button).toHaveAttribute('disabled')
    })

    it('button text changes to "Uploading..." when loading', () => {
      const mockFile = new File(['content'], 'test.zip', {
        type: 'application/zip',
      })
      renderComponent({ selectedFile: mockFile, loading: true })

      expect(screen.getByText('Uploading...')).toBeInTheDocument()
    })

    it('button shows "Upload & Notify STTs" when not loading', () => {
      renderComponent({ loading: false })

      expect(screen.getByText('Upload & Notify STTs')).toBeInTheDocument()
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

      const button = screen.getByText('Upload & Notify STTs')
      fireEvent.click(button)

      expect(mockOnUpload).toHaveBeenCalledTimes(1)
    })

    it('calls onUpload when button is clicked (validation happens in parent)', () => {
      // Button is no longer disabled without file - validation happens on click in parent component
      renderComponent({ selectedFile: null, loading: false })

      const button = screen.getByTestId('mock-button')
      fireEvent.click(button)

      // The upload function is called, parent component handles validation
      expect(mockOnUpload).toHaveBeenCalledTimes(1)
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

  describe('Date Extracted Input', () => {
    it('renders date input with correct label', () => {
      renderComponent()

      expect(
        screen.getByText('Data extracted from database on')
      ).toBeInTheDocument()
    })

    it('renders date input with hint text', () => {
      renderComponent()

      expect(screen.getByText('mm/dd/yyyy')).toBeInTheDocument()
    })

    it('renders date input field', () => {
      renderComponent()

      const dateInput = screen.getByLabelText('Data extracted from database on')
      expect(dateInput).toHaveAttribute('name', 'date-extracted-on')
      expect(dateInput).toHaveAttribute('id', 'date-extracted-on')
      // USWDS date picker wraps the input - check for wrapper
      expect(dateInput.closest('.usa-date-picker')).toBeInTheDocument()
    })

    it('allows setting date value via DOM', () => {
      renderComponent()

      // USWDS date picker is uncontrolled - set value directly on DOM
      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '2025-02-28'
      expect(dateInput.value).toBe('2025-02-28')
    })

    it('calls onDateBlur when date input loses focus', () => {
      renderComponent()

      const dateInput = screen.getByLabelText('Data extracted from database on')
      fireEvent.blur(dateInput)

      expect(mockOnDateBlur).toHaveBeenCalledTimes(1)
    })

    it('shows date error message when dateError prop is set', () => {
      const errorMessage =
        "Choose the date that the data you're uploading was extracted from the database."
      renderComponent({ dateError: errorMessage })

      const errorElement = screen.getByText(errorMessage)
      expect(errorElement).toBeInTheDocument()
      expect(errorElement).toHaveClass('usa-error-message')
      expect(errorElement).toHaveAttribute('role', 'alert')
    })

    it('applies error class to date form group when dateError is set', () => {
      const { container } = renderComponent({
        dateError: 'Date is required',
      })

      const formGroups = container.querySelectorAll('.usa-form-group')
      // Second form group is the date input
      expect(formGroups[1]).toHaveClass('usa-form-group--error')
    })

    it('does not show date error when dateError is null', () => {
      renderComponent({ dateError: null })

      expect(
        screen.queryByText(
          "Choose the date that the data you're uploading was extracted from the database."
        )
      ).not.toBeInTheDocument()
    })
  })

  describe('Ref Methods', () => {
    it('getDateValue returns ISO date from hidden input', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      // Set value on the hidden input (YYYY-MM-DD format)
      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '2025-02-28'

      expect(ref.current.getDateValue()).toBe('2025-02-28')
    })

    it('getDateValue converts MM/DD/YYYY to ISO format', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      // Set value in MM/DD/YYYY format (USWDS format)
      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '02/28/2025'

      expect(ref.current.getDateValue()).toBe('2025-02-28')
    })

    it('getDateValue returns value as-is for unknown format', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      // Set an unknown format value
      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '28-02-2025'

      expect(ref.current.getDateValue()).toBe('28-02-2025')
    })

    it('getDateValue falls back to external input when hidden input is empty', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      // Create mock external input that USWDS would create
      const externalInput = document.createElement('input')
      externalInput.className = 'usa-date-picker__external-input'
      externalInput.value = '01/15/2025'
      document.body.appendChild(externalInput)

      // Hidden input is empty
      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = ''

      expect(ref.current.getDateValue()).toBe('2025-01-15')

      // Cleanup
      document.body.removeChild(externalInput)
    })

    it('getDateValue returns empty string when both inputs are empty', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = ''

      expect(ref.current.getDateValue()).toBe('')
    })

    it('clearDate clears the hidden input', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '2025-02-28'

      ref.current.clearDate()

      expect(dateInput.value).toBe('')
    })

    it('clearDate clears the external input when it exists', () => {
      const ref = React.createRef()
      render(<FeedbackReportsUpload {...defaultProps} ref={ref} />)

      // Create mock external input that USWDS would create
      const externalInput = document.createElement('input')
      externalInput.className = 'usa-date-picker__external-input'
      externalInput.value = '02/28/2025'
      document.body.appendChild(externalInput)

      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '2025-02-28'

      ref.current.clearDate()

      expect(dateInput.value).toBe('')
      expect(externalInput.value).toBe('')

      // Cleanup
      document.body.removeChild(externalInput)
    })

    it('clearFileInput clears the file input and removes USWDS preview classes and elements', () => {
      const ref = React.createRef()
      const fileInputRef = React.createRef()
      render(
        <FeedbackReportsUpload
          {...defaultProps}
          inputRef={fileInputRef}
          ref={ref}
        />
      )

      const dropTarget = fileInputRef.current.parentNode
      dropTarget.classList.add('usa-file-input__target', 'has-invalid-file')

      const instructions = document.createElement('div')
      instructions.className = 'usa-file-input__instructions display-block'
      dropTarget.appendChild(instructions)

      ref.current.clearFileInput()

      expect(fileInputRef.current.value).toBe('')
      expect(instructions.classList.contains('display-block')).toBe(false)
      expect(dropTarget.classList.contains('has-invalid-file')).toBe(false)
    })

    it('clearFileInput handles missing instructions element and null inputRef safely', () => {
      const ref = React.createRef()
      const fileInputRef = React.createRef()
      render(
        <FeedbackReportsUpload
          {...defaultProps}
          inputRef={fileInputRef}
          ref={ref}
        />
      )

      const dropTarget = fileInputRef.current.parentNode
      dropTarget.classList.add('usa-file-input__target', 'has-invalid-file')

      ref.current.clearFileInput()
      expect(dropTarget.classList.contains('has-invalid-file')).toBe(false)

      // Also safe when inputRef.current is null
      const nullInputRef = { current: null }
      const ref2 = React.createRef()
      render(
        <FeedbackReportsUpload
          {...defaultProps}
          inputRef={nullInputRef}
          ref={ref2}
        />
      )
      nullInputRef.current = null
      expect(() => ref2.current.clearFileInput()).not.toThrow()
    })
  })

  describe('Date auto-formatting', () => {
    it('auto-inserts slashes when typing digits for MM/DD/YYYY', () => {
      expect(formatTypedDate('', '')).toBe('')
      expect(formatTypedDate('abc', '')).toBe('')
      expect(formatTypedDate('1', '')).toBe('1')
      expect(formatTypedDate('12', '1')).toBe('12/')
      expect(formatTypedDate('12/0', '12/')).toBe('12/0')
      expect(formatTypedDate('12/05', '12/0')).toBe('12/05/')
      expect(formatTypedDate('12/05/2025', '12/05/202')).toBe('12/05/2025')
      expect(formatTypedDate('12/05/20259', '12/05/2025')).toBe('12/05/2025')
    })

    it('formats pasted 8-digit dates and unslashed multi-digit input', () => {
      expect(formatTypedDate('120', '12')).toBe('12/0')
      expect(formatTypedDate('1205', '120')).toBe('12/05/')
      expect(formatTypedDate('12052025', '')).toBe('12/05/2025')
      expect(formatTypedDate('12/052025', '12/')).toBe('12/05/2025')
    })

    it('allows backspacing past auto-inserted slashes and preserves manual slashes', () => {
      expect(formatTypedDate('12', '12/')).toBe('12')
      expect(formatTypedDate('12/05', '12/05/')).toBe('12/05')
      expect(formatTypedDate('1/5/2025', '1/5/202')).toBe('1/5/2025')
    })

    it('formats input on the USWDS external date picker input as the user types', () => {
      const externalInput = document.createElement('input')
      externalInput.className = 'usa-date-picker__external-input'
      document.body.appendChild(externalInput)

      const { unmount } = renderComponent()

      fireEvent.input(externalInput, { target: { value: '12' } })
      expect(externalInput.value).toBe('12/')

      fireEvent.input(externalInput, { target: { value: '12/05' } })
      expect(externalInput.value).toBe('12/05/')

      fireEvent.input(externalInput, { target: { value: '12/05/2025' } })
      expect(externalInput.value).toBe('12/05/2025')

      unmount()
      document.body.removeChild(externalInput)
    })
  })

  describe('Notes field', () => {
    it('renders label, hint, textarea, and character counter', () => {
      renderComponent()

      expect(screen.getByText('Notes (optional)')).toBeInTheDocument()
      expect(
        screen.getByText(
          'Notes will be displayed to STTs when additional detail is needed to contextualize a report'
        )
      ).toBeInTheDocument()
      const textarea = screen.getByLabelText('Notes (optional)')
      expect(textarea).toBeInTheDocument()
      expect(textarea).toHaveAttribute('maxlength', '2000')
      expect(screen.getByText('0/2000')).toBeInTheDocument()
    })

    it('displays dynamic character count when notes prop is provided', () => {
      renderComponent({ notes: 'Testing 1 2 3' })

      expect(screen.getByText('13/2000')).toBeInTheDocument()
    })

    it('triggers onNotesChange when user types in textarea', () => {
      const mockOnNotesChange = jest.fn()
      renderComponent({ onNotesChange: mockOnNotesChange })

      const textarea = screen.getByLabelText('Notes (optional)')
      fireEvent.change(textarea, { target: { value: 'New note' } })

      expect(mockOnNotesChange).toHaveBeenCalledTimes(1)
    })

    it('displays notesError when provided', () => {
      renderComponent({
        notesError: 'HTML and JavaScript are not allowed in the notes field.',
      })

      expect(
        screen.getByText(
          'HTML and JavaScript are not allowed in the notes field.'
        )
      ).toBeInTheDocument()
    })
  })
})
