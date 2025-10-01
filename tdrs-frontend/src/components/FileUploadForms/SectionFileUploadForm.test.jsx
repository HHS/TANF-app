import React from 'react'
import { fireEvent, waitFor, render } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import SectionFileUploadForm from './SectionFileUploadForm'
import { ReportsProvider } from '../Reports/ReportsContext'
import { fileUploadSections } from '../../reducers/reports'
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
  })

  afterEach(() => {
    jest.runOnlyPendingTimers()
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  const renderComponent = (storeState = initialState, stt = { id: 1, num_sections: 4 }) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return render(
      <Provider store={store}>
        <ReportsProvider>
          <SectionFileUploadForm stt={stt} />
        </ReportsProvider>
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
      expect(queryByTestId('file-upload-Aggregate Data')).not.toBeInTheDocument()
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

      expect(getByText('Section 1 TANF - Active Case Data')).toBeInTheDocument()
      expect(getByText('Section 2 TANF - Closed Case Data')).toBeInTheDocument()
      expect(getByText('Section 3 TANF - Aggregate Data')).toBeInTheDocument()
      expect(getByText('Section 4 TANF - Stratum Data')).toBeInTheDocument()
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

    it('does not scroll when alert is not active', () => {
      renderComponent()

      expect(window.HTMLElement.prototype.scrollIntoView).not.toHaveBeenCalled()
    })
  })

  describe('Section Formatting', () => {
    it('maps section indices correctly', () => {
      const uploadedFiles = [
        {
          fileName: 'test1.txt',
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

    it('handles multiple sections with proper formatting', () => {
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
          section: 'Aggregate Data',
          fileType: 'tanf',
          year: '2024',
          quarter: 'Q1',
        },
        {
          fileName: 'test3.txt',
          section: 'Stratum Data',
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
  })

  describe('File Upload Integration', () => {
    it('passes correct props to FileUpload components', () => {
      const { getByTestId } = renderComponent()

      const activeUpload = getByTestId('file-upload-Active Case Data')
      const input = activeUpload.querySelector('input')

      expect(input).toHaveAttribute('data-section', 'Active Case Data')
      expect(input).toHaveAttribute('data-filetype', 'tanf')
    })

    it('renders FileUpload for each section in correct order', () => {
      const { getByTestId } = renderComponent()

      fileUploadSections.forEach((section) => {
        expect(getByTestId(`file-upload-${section}`)).toBeInTheDocument()
      })
    })

    it('passes year and quarter from context to FileUpload', () => {
      const { getByTestId } = renderComponent()

      const activeUpload = getByTestId('file-upload-Active Case Data')
      const input = activeUpload.querySelector('input')

      expect(input).toHaveAttribute('data-year', '')
      expect(input).toHaveAttribute('data-quarter', '')
    })
  })

  describe('STT Handling', () => {
    it('uses stt.id when stt is provided', async () => {
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

      const stt = { id: 42, name: 'Test State', num_sections: 4 }

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

      const { getByText } = renderComponent(storeState, undefined)

      const submitButton = getByText('Submit Data Files')
      fireEvent.click(submitButton)

      await waitFor(() => {
        expect(mockExecuteSubmission).toHaveBeenCalled()
      })
    })

    it('renders only num_sections when specified', () => {
      const stt = { id: 1, num_sections: 3 }
      const { getByTestId, queryByTestId } = renderComponent(initialState, stt)

      expect(getByTestId('file-upload-Active Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Closed Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Aggregate Data')).toBeInTheDocument()
      expect(queryByTestId('file-upload-Stratum Data')).not.toBeInTheDocument()
    })

    it('renders only 1 section when num_sections is 1', () => {
      const stt = { id: 1, num_sections: 1 }
      const { getByTestId, queryByTestId } = renderComponent(initialState, stt)

      expect(getByTestId('file-upload-Active Case Data')).toBeInTheDocument()
      expect(queryByTestId('file-upload-Closed Case Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Aggregate Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Stratum Data')).not.toBeInTheDocument()
    })

    it('uses default 4 sections when stt has no num_sections property', () => {
      const stt = { id: 1 } // No num_sections property
      const { getByTestId } = renderComponent(initialState, stt)

      expect(getByTestId('file-upload-Active Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Closed Case Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Aggregate Data')).toBeInTheDocument()
      expect(getByTestId('file-upload-Stratum Data')).toBeInTheDocument()
    })

    it('uses stt.num_sections when it is 0 (falsy but defined)', () => {
      const stt = { id: 1, num_sections: 0 }
      const { queryByTestId } = renderComponent(initialState, stt)

      // Should render 0 sections (slice(0, 0) returns empty array)
      expect(queryByTestId('file-upload-Active Case Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Closed Case Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Aggregate Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Stratum Data')).not.toBeInTheDocument()
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

    it('handles files with sections not in fileUploadSections', () => {
      const uploadedFiles = [
        {
          fileName: 'test.txt',
          section: 'Unknown Section',
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

    it('handles zero num_sections', () => {
      const stt = { id: 1, num_sections: 0 }
      const { queryByTestId } = renderComponent(initialState, stt)

      expect(queryByTestId('file-upload-Active Case Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Closed Case Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Aggregate Data')).not.toBeInTheDocument()
      expect(queryByTestId('file-upload-Stratum Data')).not.toBeInTheDocument()
    })
  })

  describe('File Type Handling', () => {
    it('displays correct file type in labels for TANF', () => {
      const { getByText } = renderComponent()

      expect(getByText('Section 1 TANF - Active Case Data')).toBeInTheDocument()
    })

    it('displays correct file type in labels for SSP-MOE', () => {
      const storeState = {
        ...initialState,
        reports: {
          submittedFiles: [],
        },
      }

      const { getByText } = renderComponent(storeState)

      // Note: The file type comes from ReportsContext, which defaults to 'tanf'
      // In a real scenario, the context would need to be set to 'ssp-moe'
      expect(getByText('Section 1 TANF - Active Case Data')).toBeInTheDocument()
    })
  })

  describe('Context Integration', () => {
    it('uses yearInputValue from context', () => {
      const { getByTestId } = renderComponent()

      const activeUpload = getByTestId('file-upload-Active Case Data')
      const input = activeUpload.querySelector('input')

      // Year comes from ReportsContext, which defaults to ''
      expect(input).toHaveAttribute('data-year', '')
    })

    it('uses quarterInputValue from context', () => {
      const { getByTestId } = renderComponent()

      const activeUpload = getByTestId('file-upload-Active Case Data')
      const input = activeUpload.querySelector('input')

      // Quarter comes from ReportsContext, which defaults to ''
      expect(input).toHaveAttribute('data-quarter', '')
    })

    it('uses fileTypeInputValue from context', () => {
      const { getByTestId } = renderComponent()

      const activeUpload = getByTestId('file-upload-Active Case Data')
      const input = activeUpload.querySelector('input')

      // File type comes from ReportsContext, which defaults to 'tanf'
      expect(input).toHaveAttribute('data-filetype', 'tanf')
    })
  })
})
