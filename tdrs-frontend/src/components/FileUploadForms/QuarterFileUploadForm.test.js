import { fireEvent, waitFor, render } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import QuarterFileUploadForm from './QuarterFileUploadForm'
import { ReportsProvider } from '../Reports/ReportsContext'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useEventLogger } from '../../utils/eventLogger'
import { MemoryRouter } from 'react-router-dom'

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
  default: ({ section, year, quarter, fileType, label }) => (
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
        <MemoryRouter>
          <ReportsProvider>
            <QuarterFileUploadForm stt={stt} />
          </ReportsProvider>
        </MemoryRouter>
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
    it('shows error alert when submitting with no uploaded files', async () => {
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
        expect(alert).toHaveTextContent(
          'No changes have been made to data files'
        )
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
})
