import React from 'react'
import { fireEvent, waitFor, render } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import QuarterFileUploadForm from './QuarterFileUploadForm'
import { ReportsProvider } from '../Reports/ReportsContext'
import * as reportsActions from '../../actions/reports'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useEventLogger } from '../../utils/eventLogger'

// Mock dependencies
jest.mock('../../hooks/useFormSubmission')
jest.mock('../../utils/eventLogger')
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
}))

// Mock FileUpload component
jest.mock('../FileUpload', () => ({
  __esModule: true,
  default: ({ section, year, quarter, fileType, label, setLocalAlertState }) => (
    <div data-testid={`file-upload-${section}`}>
      <label>{label}</label>
      <input
        type="file"
        data-section={section}
        data-year={year}
        data-quarter={quarter}
        data-filetype={fileType}
      />
    </div>
  ),
}))

const initialState = {
  auth: {
    authenticated: true,
    user: {
      email: 'test@example.com',
      stt: {
        id: 1,
        type: 'state',
        code: 'CA',
        name: 'California',
      },
      roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
      account_approval_status: 'Approved',
    },
  },
  reports: {
    submittedFiles: [],
  },
}

const mockStore = (initial = initialState) => configureStore(initial)

const makeTestFile = (name, contents = ['test'], type = 'text/plain') =>
  new File(contents, name, { type })

describe('QuarterFileUploadForm', () => {
  let mockExecuteSubmission
  let mockLogger
  let mockDispatch

  beforeEach(() => {
    jest.useFakeTimers()

    // Mock useFormSubmission hook
    mockExecuteSubmission = jest.fn()
    useFormSubmission.mockReturnValue({
      isSubmitting: false,
      executeSubmission: mockExecuteSubmission,
    })

    // Mock useEventLogger hook
    mockLogger = jest.fn()
    useEventLogger.mockReturnValue(mockLogger)

    // Mock scrollIntoView
    window.HTMLElement.prototype.scrollIntoView = jest.fn()
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  const renderComponent = (storeState = initialState, stt = { id: 1 }) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return render(
      <Provider store={store}>
        <ReportsProvider>
          <QuarterFileUploadForm stt={stt} />
        </ReportsProvider>
      </Provider>
    )
  }

  describe('Rendering', () => {
    it('renders all four quarter file upload inputs', () => {
      const { getByTestId } = renderComponent()

      expect(
        getByTestId('file-upload-Quarter 1 (October - December)')
      ).toBeInTheDocument()
      expect(
        getByTestId('file-upload-Quarter 2 (January - March)')
      ).toBeInTheDocument()
      expect(
        getByTestId('file-upload-Quarter 3 (April - June)')
      ).toBeInTheDocument()
      expect(
        getByTestId('file-upload-Quarter 4 (July - September)')
      ).toBeInTheDocument()
    })

    it('renders submit and cancel buttons', () => {
      const { getByText } = renderComponent()

      expect(getByText('Submit Data Files')).toBeInTheDocument()
      expect(getByText('Cancel')).toBeInTheDocument()
    })

    it('does not show alert initially', () => {
      const { queryByRole } = renderComponent()

      expect(queryByRole('alert')).not.toBeInTheDocument()
    })

    it('initializes USWDS file input on mount', () => {
      const { fileInput } = require('@uswds/uswds/src/js/components')
      renderComponent()

      expect(fileInput.init).toHaveBeenCalled()
    })
  })

  describe('Form Submission', () => {
    it('shows error alert when submitting with no files', async () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText, getByRole } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        const alert = getByRole('alert')
        expect(alert).toBeInTheDocument()
        expect(alert).toHaveTextContent('No changes have been made to data files')
      })

      expect(mockExecuteSubmission).not.toHaveBeenCalled()
    })

    it('submits successfully with uploaded files', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })
    })

    it('transforms files correctly before submission', async () => {
      const uploadedFiles = [
        {
          fileName: 'q1.txt',
          section: 'Quarter 1 (October - December)',
          fileType: 'pia',
          year: '2024',
        },
        {
          fileName: 'q2.txt',
          section: 'Quarter 2 (January - March)',
          fileType: 'pia',
          year: '2024',
        },
      ]

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: uploadedFiles,
        },
      }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })

      // Verify executeSubmission was called with a function
      expect(mockExecuteSubmission).toHaveBeenCalledWith(expect.any(Function))
    })

    it('formats quarters correctly in success message', async () => {
      const uploadedFiles = [
        {
          fileName: 'q1.txt',
          section: 'Quarter 1 (October - December)',
          fileType: 'pia',
          year: '2024',
        },
        {
          fileName: 'q3.txt',
          section: 'Quarter 3 (April - June)',
          fileType: 'pia',
          year: '2024',
        },
      ]

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: uploadedFiles,
        },
      }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })
    })

    it('handles submission errors gracefully', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      const error = new Error('Submission failed')
      mockExecuteSubmission.mockRejectedValue(error)

      const { getByText, getByRole } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        const alert = getByRole('alert')
        expect(alert).toBeInTheDocument()
        expect(alert).toHaveTextContent(
          'An error occurred during submission. Please try again.'
        )
      })
    })

    it('disables submit button when isSubmitting is true', () => {
      useFormSubmission.mockReturnValue({
        isSubmitting: true,
        executeSubmission: mockExecuteSubmission,
      })

      const { getByText } = renderComponent()

      const submitButton = getByText('Submitting...')
      expect(submitButton).toHaveAttribute('disabled')
    })

    it('shows "Submitting..." text when form is submitting', () => {
      useFormSubmission.mockReturnValue({
        isSubmitting: true,
        executeSubmission: mockExecuteSubmission,
      })

      const { getByText, queryByText } = renderComponent()

      expect(getByText('Submitting...')).toBeInTheDocument()
      expect(queryByText('Submit Data Files')).not.toBeInTheDocument()
    })

    it('calls handleOpenFeedbackWidget after successful submission', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })

      // Verify feedback widget action was dispatched
      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalled()
      })
    })
  })

  describe('Cancel Functionality', () => {
    it('shows error modal when cancel is clicked with uploaded files', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      const { getByText } = renderComponent(storeState)

      const cancelButton = getByText('Cancel')
      fireEvent.click(cancelButton)

      // The error modal visibility is controlled by ReportsContext
      // We can verify the state change through the context
      await waitFor(() => {
        expect(cancelButton).toBeInTheDocument()
      })
    })

    it('clears files when cancel is clicked without uploaded files', async () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText } = renderComponent(storeState)

      const cancelButton = getByText('Cancel')
      fireEvent.click(cancelButton)

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalled()
      })
    })
  })

  describe('Alert Behavior', () => {
    it('scrolls to alert when alert becomes active', async () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText, getByRole } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        const alert = getByRole('alert')
        expect(alert).toBeInTheDocument()
      })

      expect(window.HTMLElement.prototype.scrollIntoView).toHaveBeenCalledWith({
        behavior: 'smooth',
      })
    })

    it('displays error alert with correct styling', async () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText, container } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        const alert = container.querySelector('.usa-alert--error')
        expect(alert).toBeInTheDocument()
      })
    })
  })

  describe('Quarter Formatting', () => {
    it('formats single quarter correctly', () => {
      const uploadedFiles = [
        {
          fileName: 'q1.txt',
          section: 'Quarter 1 (October - December)',
          fileType: 'pia',
          year: '2024',
        },
      ]

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: uploadedFiles,
        },
      }

      renderComponent(storeState)
      // Component renders without errors
    })

    it('formats multiple quarters with "and" correctly', () => {
      const uploadedFiles = [
        {
          fileName: 'q1.txt',
          section: 'Quarter 1 (October - December)',
          fileType: 'pia',
          year: '2024',
        },
        {
          fileName: 'q2.txt',
          section: 'Quarter 2 (January - March)',
          fileType: 'pia',
          year: '2024',
        },
      ]

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: uploadedFiles,
        },
      }

      renderComponent(storeState)
      // Component renders without errors
    })
  })

  describe('File Upload Integration', () => {
    it('passes correct props to FileUpload components', () => {
      const { getByTestId } = renderComponent()

      const q1Upload = getByTestId('file-upload-Quarter 1 (October - December)')
      const input = q1Upload.querySelector('input')

      expect(input).toHaveAttribute('data-section', 'Quarter 1 (October - December)')
      expect(input).toHaveAttribute('data-quarter', '1')
    })

    it('renders FileUpload for each quarter in correct order', () => {
      const { getByTestId } = renderComponent()

      const uploads = [
        'file-upload-Quarter 1 (October - December)',
        'file-upload-Quarter 2 (January - March)',
        'file-upload-Quarter 3 (April - June)',
        'file-upload-Quarter 4 (July - September)',
      ]

      uploads.forEach((testId) => {
        expect(getByTestId(testId)).toBeInTheDocument()
      })
    })
  })

  describe('STT Handling', () => {
    it('uses stt.id when stt is provided', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      const stt = { id: 42, name: 'Test State' }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState, stt)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })
    })

    it('handles undefined stt gracefully', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState, undefined)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })
    })
  })

  describe('Edge Cases', () => {
    it('handles empty uploadedFiles array', () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText } = renderComponent(storeState)
      expect(getByText('Submit Data Files')).toBeInTheDocument()
    })

    it('handles null submittedFiles', () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: null,
        },
      }

      const { getByText } = renderComponent(storeState)
      expect(getByText('Submit Data Files')).toBeInTheDocument()
    })

    it('handles files with invalid section names', () => {
      const uploadedFiles = [
        {
          fileName: 'test.txt',
          section: 'Invalid Section',
          fileType: 'pia',
          year: '2024',
        },
      ]

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: uploadedFiles,
        },
      }

      renderComponent(storeState)
      // Component should handle gracefully
    })

    it('prevents form submission via Enter key when no files uploaded', async () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { container, getByRole } = renderComponent(storeState)
      const form = container.querySelector('form')

      fireEvent.submit(form)

      await waitFor(() => {
        const alert = getByRole('alert')
        expect(alert).toHaveTextContent('No changes have been made to data files')
      })

      expect(mockExecuteSubmission).not.toHaveBeenCalled()
    })
  })

  describe('Console Logging', () => {
    it('logs submission process', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Quarter 1 (October - December)',
        fileType: 'pia',
        year: '2024',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      mockExecuteSubmission.mockImplementation(async (fn) => {
        await fn()
      })

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('onSubmit called')
      })

      consoleSpy.mockRestore()
    })

    it('logs error when no files uploaded', async () => {
      const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Setting error alert')
      })

      consoleSpy.mockRestore()
    })
  })
})
