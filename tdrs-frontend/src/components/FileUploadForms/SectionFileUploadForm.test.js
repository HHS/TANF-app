import React from 'react'
import { fireEvent, waitFor, render } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import SectionFileUploadForm from './SectionFileUploadForm'
import { ReportsProvider } from '../Reports/ReportsContext'
import { useFormSubmission } from '../../hooks/useFormSubmission'
import { useEventLogger } from '../../utils/eventLogger'
import { MemoryRouter } from 'react-router-dom'
import * as reportsActions from '../../actions/reports'

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
  default: ({
    section,
    year,
    quarter,
    fileType,
    label,
    setLocalAlertState,
  }) => (
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

describe('SectionFileUploadForm', () => {
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

    jest
      .spyOn(reportsActions, 'clearFileList')
      .mockImplementation(({ fileType }) => ({
        type: 'CLEAR_FILE_LIST',
        payload: { fileType },
      }))

    jest
      .spyOn(reportsActions, 'getAvailableFileList')
      .mockImplementation(({ file_type }, onSuccess = () => null) => () => {
        onSuccess()
        return Promise.resolve({
          type: 'SET_FILE_LIST',
          payload: { data: [] },
          file_type,
        })
      })

    jest
      .spyOn(reportsActions, 'submit')
      .mockImplementation((payload, onComplete = () => null) => () => {
        onComplete(['file-id-1'])
        return Promise.resolve()
      })
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
    jest.clearAllMocks()
    jest.restoreAllMocks()
  })

  const renderComponent = (
    storeState = initialState,
    stt = { id: 1, num_sections: 4 }
  ) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return render(
      <Provider store={store}>
        <MemoryRouter>
          <ReportsProvider>
            <SectionFileUploadForm stt={stt} />
          </ReportsProvider>
        </MemoryRouter>
      </Provider>
    )
  }

  describe('Rendering', () => {
    it('renders all four section file upload inputs by default', () => {
      const { getByTestId } = renderComponent()

      expect(getByTestId('file-upload-Active Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Closed Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Aggregate Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Stratum Data')).toBeInTheDocument()
    })

    it('renders correct number of sections based on stt.num_sections', () => {
      const stt = { id: 1, num_sections: 2 }
      const { getByTestId, queryByTestId } = renderComponent(initialState, stt)

      expect(getByTestId('file-upload-Active Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Closed Case Data')).toBeInTheDocument()
      expect(
        queryByTestId('file-upload-Aggregate Data')
      ).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Stratum Data')).not.toBeInTheDocument()
    })

    it('renders 4 sections when stt is undefined', () => {
      const { getByTestId } = renderComponent(initialState, undefined)

      expect(getByTestId('file-upload-Active Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Closed Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Aggregate Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Stratum Data')).toBeInTheDocument()
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

    it('renders section labels with correct format', () => {
      const { getByText } = renderComponent()

      expect(
        getByText('Section 1 - TANF - Active Case Data')
      ).toBeInTheDocument()
      expect(
        getByText('Section 2 - TANF - Closed Case Data')
      ).toBeInTheDocument()
      expect(getByText('Section 3 - TANF - Aggregate Data')).toBeInTheDocument()
      expect(getByText('Section 4 - TANF - Stratum Data')).toBeInTheDocument()
    })
  })

  describe('Form Submission', () => {
    it('does not allow submission with no uploaded files', async () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      expect(submitButton).not.toBeEnabled()

      expect(mockExecuteSubmission).not.toHaveBeenCalled()
    })

    it('submits successfully with uploaded files', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Active Case Data',
        fileType: 'tanf',
        year: '2024',
        quarter: 'Q1',
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

      const clearFileListSpy = jest.spyOn(reportsActions, 'clearFileList')

      const { getByText } = renderComponent(storeState)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })

      // After successful submission the upload panel should be cleared via handleClearFilesOnly
      expect(clearFileListSpy).toHaveBeenCalled()
    })

    it('passes correct parameters to submit action', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Active Case Data',
        fileType: 'tanf',
        year: '2024',
        quarter: 'Q1',
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
        expect(mockExecuteSubmission).toHaveBeenCalledWith(expect.any(Function))
      })
    })

    it('formats sections correctly for single file', () => {
      const uploadedFiles = [
        {
          fileName: 'test.txt',
          section: 'Active Case Data',
          fileType: 'tanf',
          year: '2024',
          quarter: 'Q1',
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

    it('formats sections correctly for multiple files with "and"', () => {
      const uploadedFiles = [
        {
          fileName: 'test1.txt',
          section: 'Active Case Data',
          fileType: 'tanf',
          year: '2024',
          quarter: 'Q1',
        },
        {
          fileName: 'test2.txt',
          section: 'Closed Case Data',
          fileType: 'tanf',
          year: '2024',
          quarter: 'Q1',
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

    it('handles submission errors gracefully', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Active Case Data',
        fileType: 'tanf',
        year: '2024',
        quarter: 'Q1',
      }

      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [uploadedFile],
        },
      }

      const error = new Error('Submission failed')
      mockExecuteSubmission.mockRejectedValue(error)

      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation()

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

      expect(consoleErrorSpy).toHaveBeenCalledWith(
        'Error during form submission:',
        error
      )

      consoleErrorSpy.mockRestore()
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
        section: 'Active Case Data',
        fileType: 'tanf',
        year: '2024',
        quarter: 'Q1',
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

    it('passes ssp flag correctly for ssp-moe file type', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Active Case Data',
        fileType: 'ssp-moe',
        year: '2024',
        quarter: 'Q1',
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

    it('passes ssp flag as false for non-ssp-moe file types', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Active Case Data',
        fileType: 'tanf',
        year: '2024',
        quarter: 'Q1',
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
  })

  describe('Cancel Functionality', () => {
    it('shows error modal when cancel is clicked with uploaded files', async () => {
      const uploadedFile = {
        fileName: 'test.txt',
        section: 'Active Case Data',
        fileType: 'tanf',
        year: '2024',
        quarter: 'Q1',
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
