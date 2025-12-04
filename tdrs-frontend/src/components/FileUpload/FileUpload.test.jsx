import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import FileUpload from './FileUpload'
import * as reportsActions from '../../actions/reports'
import * as utils from './utils'
import fileTypeChecker from 'file-type-checker'

// Mock dependencies
jest.mock('file-type-checker')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('./utils', () => ({
  handlePreview: jest.fn(),
  getTargetClassName: jest.fn((name) => `.target-${name}`),
  tryGetUTF8EncodedFile: jest.fn(),
  validateHeader: jest.fn(),
  checkPreviewDependencies: jest.fn(),
  removeOldPreviews: jest.fn(),
}))

const initialState = {
  reports: {
    submittedFiles: [
      {
        section: 'Active Case Data',
        fileName: null,
        error: null,
        uuid: null,
        name: null,
      },
    ],
  },
}

const mockStore = (initial = initialState) => configureStore(initial)

const makeTestFile = (name, contents = 'test content', type = 'text/plain') =>
  new File([contents], name, { type })

describe('FileUpload', () => {
  let mockSetLocalAlertState
  let mockDispatch

  beforeEach(() => {
    mockSetLocalAlertState = jest.fn()
    jest.clearAllMocks()

    // Mock FileReader
    global.FileReader = jest.fn(() => ({
      readAsArrayBuffer: jest.fn(function () {
        this.onload()
      }),
      result: new ArrayBuffer(8),
      onerror: jest.fn(),
      abort: jest.fn(),
    }))

    // Default mock implementations
    fileTypeChecker.validateFileType.mockReturnValue(false)
    utils.handlePreview.mockReturnValue(true)
    utils.checkPreviewDependencies.mockReturnValue({
      rendered: true,
      dropTarget: document.createElement('div'),
      instructions: document.createElement('div'),
    })
    utils.tryGetUTF8EncodedFile.mockResolvedValue({
      encodedFile: makeTestFile('test.txt'),
      header: 'HEADER20241A06   TAN1ED',
    })
    utils.validateHeader.mockResolvedValue({
      isValid: true,
      calendarFiscalResult: { isValid: true },
      programTypeResult: { isValid: true },
    })
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  const renderComponent = (
    storeState = initialState,
    props = {
      section: 'Active Case Data',
      year: '2024',
      quarter: 'Q1',
      fileType: 'tanf',
      label: 'Active Case Data',
      setLocalAlertState: mockSetLocalAlertState,
    }
  ) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return render(
      <Provider store={store}>
        <FileUpload {...props} />
      </Provider>
    )
  }

  describe('Rendering', () => {
    it('does not render error message when no error', () => {
      const { queryByRole } = renderComponent()

      expect(queryByRole('alert')).not.toBeInTheDocument()
    })

    it('renders error message when error exists', () => {
      const stateWithError = {
        reports: {
          submittedFiles: [
            {
              section: 'Active Case Data',
              fileName: null,
              error: { message: 'Invalid file type' },
              uuid: null,
              name: null,
            },
          ],
        },
      }

      const { getByRole } = renderComponent(stateWithError)

      const alert = getByRole('alert')
      expect(alert).toHaveTextContent('Invalid file type')
    })

    it('renders error message with link when provided', () => {
      const stateWithError = {
        reports: {
          submittedFiles: [
            {
              section: 'Active Case Data',
              fileName: null,
              error: {
                message: 'Invalid file',
                link: <a href="/help">Need help?</a>,
              },
              uuid: null,
              name: null,
            },
          ],
        },
      }

      const { getByRole, getByText } = renderComponent(stateWithError)

      expect(getByRole('alert')).toBeInTheDocument()
      expect(getByText('Need help?')).toBeInTheDocument()
    })
  })

  describe('File Selection', () => {
    it('clears alert state when file is selected', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockSetLocalAlertState).toHaveBeenCalledWith({
          active: false,
          type: null,
          message: null,
        })
      })
    })
  })

  describe('File Validation - Extension', () => {
    it('accepts .txt files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('accepts .ms## files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.ms01')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('accepts .ts## files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.ts06')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('accepts .ts### files', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.ts123')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('rejects files with invalid extensions', async () => {
      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.pdf')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.FILE_EXT_ERROR,
          })
        )
      })
    })

    it('rejects image files (png)', async () => {
      // Reset the mock and set it to return true for this specific test
      fileTypeChecker.validateFileType.mockReset()
      fileTypeChecker.validateFileType.mockReturnValue(true)

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt') // Has valid extension but is actually an image

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        const errorCalls = mockDispatch.mock.calls.filter(
          (call) => call[0].type === reportsActions.SET_FILE_ERROR
        )
        expect(errorCalls.length).toBeGreaterThan(0)
        // Verify the error was dispatched (message is INVALID_FILE_ERROR constant)
        expect(errorCalls[0][0].payload.section).toBe('Active Case Data')
      })

      // Reset back to false for other tests
      fileTypeChecker.validateFileType.mockReturnValue(false)
    })
  })

  describe('File Validation - Header', () => {
    it('uploads file when header validation passes', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: true,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: true },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // The upload action is a thunk, so we check if dispatch was called with a function
        const uploadCalls = mockDispatch.mock.calls.filter(
          (call) => typeof call[0] === 'function'
        )
        expect(uploadCalls.length).toBeGreaterThan(0)
      })
    })

    it('shows program type error when program type validation fails', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: false, progType: 'SSP' },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              error: expect.objectContaining({
                message: expect.stringContaining('File may correspond to SSP instead of TAN'),
              }),
            }),
          })
        )
      })
    })

    it('shows null program type error when program type cannot be determined', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: { isValid: true },
        programTypeResult: { isValid: false, progType: null },
      })

      const { container, getByText } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        // Check that the error message text is displayed
        expect(getByText(/Could not determine the file type/i)).toBeInTheDocument()

        // Check that the help link is present
        const helpLink = container.querySelector('a[aria-label="Need help? Read header record guidance"]')
        expect(helpLink).toBeInTheDocument()
        expect(helpLink).toHaveAttribute('href', 'https://acf.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf')

        // Verify the action was dispatched with the correct type
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              section: 'Active Case Data',
            }),
          })
        )
      })
    })

    it('shows calendar/fiscal year error when validation fails', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: {
          isValid: false,
          fileFiscalYear: '2023',
          fileFiscalQuarter: '1',
        },
        programTypeResult: { isValid: true },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              error: expect.objectContaining({
                message: expect.stringContaining('Oct 1 - Dec 31'),
              }),
            }),
          })
        )
      })
    })

    it('handles default case for unknown quarter', async () => {
      utils.validateHeader.mockResolvedValue({
        isValid: false,
        calendarFiscalResult: {
          isValid: false,
          fileFiscalYear: '2023',
          fileFiscalQuarter: '5', // Invalid quarter
        },
        programTypeResult: { isValid: true },
      })

      const { container } = renderComponent()

      const input = container.querySelector('input[type="file"]')
      const file = makeTestFile('test.txt')

      fireEvent.change(input, { target: { files: [file] } })

      await waitFor(() => {
        expect(mockDispatch).toHaveBeenCalledWith(
          expect.objectContaining({
            type: reportsActions.SET_FILE_ERROR,
            payload: expect.objectContaining({
              error: expect.objectContaining({
                message: expect.stringContaining('Fiscal Year 2023'),
              }),
            }),
          })
        )
      })
    })
  })
})
