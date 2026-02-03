import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import AdminFeedbackReports from './AdminFeedbackReports'
import axiosInstance from '../../axios-instance'

jest.mock('../../axios-instance')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
  datePicker: {
    init: jest.fn(),
  },
}))

const mockStore = configureStore([thunk])

describe('AdminFeedbackReports', () => {
  let store

  beforeEach(() => {
    store = mockStore({
      auth: {
        user: {
          id: 1,
          email: 'admin@example.com',
          roles: [{ name: 'OFA Admin' }],
        },
        authenticated: true,
      },
    })

    // Reset all mocks before each test
    jest.clearAllMocks()

    // Mock successful history fetch by default
    axiosInstance.get.mockResolvedValue({ data: { results: [] } })

    // Mock FileReader for async file handling
    global.FileReader = jest.fn().mockImplementation(() => ({
      readAsArrayBuffer: jest.fn(function () {
        setTimeout(() => this.onload && this.onload(), 0)
      }),
      result: new ArrayBuffer(8),
    }))
  })

  const renderComponent = () => {
    return render(
      <MemoryRouter>
        <Provider store={store}>
          <AdminFeedbackReports />
        </Provider>
      </MemoryRouter>
    )
  }

  // Helper to select fiscal year
  const selectFiscalYear = async (year = '2025') => {
    const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
    fireEvent.change(fiscalYearSelect, { target: { value: year } })
    await waitFor(() => {
      expect(
        screen.getByText(`Fiscal Year ${year} — Upload Feedback Reports`)
      ).toBeInTheDocument()
    })
  }

  // Helper to set date input value (uncontrolled input needs direct DOM manipulation)
  const setDateInputValue = (value) => {
    const dateInput = document.getElementById('date-extracted-on')
    dateInput.value = value
    fireEvent.change(dateInput, { target: { value } })
  }

  // Helper to select a file and wait for it to be processed
  const selectFile = async (filename = 'FY2025.zip') => {
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['content'], filename, { type: 'application/zip' })
    fireEvent.change(fileInput, { target: { files: [file] } })
    // Wait for file to be registered in component state (aria description updates)
    await waitFor(() => {
      expect(
        screen.getByText(new RegExp(`Selected File ${filename}`))
      ).toBeInTheDocument()
    })
  }

  describe('Component Rendering', () => {
    it('renders the page description', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(/Once submitted, TDP will distribute/)
        ).toBeInTheDocument()
      })
    })

    it('renders fiscal year selector', async () => {
      renderComponent()

      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()
        expect(screen.getByText('- Select Fiscal Year -')).toBeInTheDocument()
      })
    })

    it('does not show upload section until fiscal year is selected', async () => {
      renderComponent()

      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toBeInTheDocument()
      })

      // File upload section should not be visible
      expect(screen.queryByText('Feedback Reports ZIP')).not.toBeInTheDocument()
      expect(screen.queryByText('Upload History')).not.toBeInTheDocument()
    })

    it('shows upload section after fiscal year is selected', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      // Wait for upload history to finish loading
      await waitFor(() => {
        expect(screen.getByText('Upload History')).toBeInTheDocument()
      })
    })

    it('renders H2 header with selected fiscal year', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      expect(
        screen.getByText('Fiscal Year 2025 — Upload Feedback Reports')
      ).toBeInTheDocument()
    })

    it('renders the date extracted input after fiscal year selected', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      expect(
        screen.getByText('Data extracted from database on')
      ).toBeInTheDocument()
      expect(screen.getByText('mm/dd/yyyy')).toBeInTheDocument()
    })
  })

  describe('File Upload Functionality', () => {
    it('shows error when non-.zip file is selected', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.txt', { type: 'text/plain' })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(
          screen.getByText('Invalid file. Make sure to select a zip file.')
        ).toBeInTheDocument()
      })
    })

    it('shows error when file FY does not match selected FY', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'FY2024_12012024.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(
          screen.getByText(
            "Your file's Fiscal Year does not match the selected Fiscal Year for this upload."
          )
        ).toBeInTheDocument()
      })
    })

    it('accepts file when FY matches selected FY', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'FY2025_02282025.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(
          screen.queryByText(
            "Your file's Fiscal Year does not match the selected Fiscal Year for this upload."
          )
        ).not.toBeInTheDocument()
      })
    })

    it('shows date error when upload clicked without date', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'FY2025.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(screen.queryByText('Invalid file.')).not.toBeInTheDocument()
      })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText(
            "Choose the date that the data you're uploading was extracted from the database."
          )
        ).toBeInTheDocument()
      })
    })

    it('shows file error when upload clicked without file', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByText('No file selected.')).toBeInTheDocument()
      })
    })

    it('successfully uploads a file with date and shows success message', async () => {
      axiosInstance.post.mockResolvedValue({
        data: {
          id: 1,
          status: 'PENDING',
          original_filename: 'FY2025.zip',
        },
      })

      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderComponent()

      await selectFiscalYear('2025')

      // Select a file and wait for it to be processed
      await selectFile('FY2025.zip')

      // Set date (using helper for uncontrolled input)
      setDateInputValue('2025-02-28')

      // Click upload
      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText(
            /Feedback report uploaded successfully! Processing has begun/
          )
        ).toBeInTheDocument()
      })

      // Verify POST was called with year and date
      expect(axiosInstance.post).toHaveBeenCalledWith(
        expect.stringContaining('/reports/report-sources/'),
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true,
        })
      )
    })

    it('shows error message when upload fails', async () => {
      axiosInstance.post.mockRejectedValue({
        response: {
          data: {
            file: ['Invalid zip file structure'],
          },
        },
      })

      renderComponent()

      await selectFiscalYear('2025')

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText('Invalid zip file structure')
        ).toBeInTheDocument()
      })
    })

    it('shows loading state during upload', async () => {
      axiosInstance.post.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      renderComponent()

      await selectFiscalYear('2025')

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /Uploading.../i })
        ).toBeInTheDocument()
      })
    })
  })

  describe('Upload History', () => {
    it('fetches history when fiscal year is selected', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
        expect(screen.getByText('02/28/2025')).toBeInTheDocument()
      })

      expect(axiosInstance.get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/report-sources/'),
        expect.objectContaining({
          params: { year: '2025' },
          withCredentials: true,
        })
      )
    })

    it('displays empty state when no history exists', async () => {
      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('No data available.')).toBeInTheDocument()
      })
    })

    it('displays error alert when history fetch fails', async () => {
      axiosInstance.get.mockRejectedValue(new Error('Failed to fetch'))

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(
          screen.getByText(
            'Failed to load upload history. Please refresh the page.'
          )
        ).toBeInTheDocument()
      })
    })

    it('refreshes history when fiscal year changes', async () => {
      const mockHistory2025 = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
      ]

      const mockHistory2024 = [
        {
          id: 2,
          year: 2024,
          date_extracted_on: '2024-12-15',
          created_at: '2024-12-20T10:31:00Z',
          processed_at: '2024-12-20T10:41:00Z',
          original_filename: 'FY2024.zip',
          file: 'https://example.com/FY2024.zip',
        },
      ]

      // Use mockImplementation to handle different year params
      axiosInstance.get.mockImplementation((url, config) => {
        const year = config?.params?.year
        if (year === '2025') {
          return Promise.resolve({ data: { results: mockHistory2025 } })
        }
        if (year === '2024') {
          return Promise.resolve({ data: { results: mockHistory2024 } })
        }
        return Promise.resolve({ data: { results: [] } })
      })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
      })

      // Change fiscal year
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2024' } })

      await waitFor(() => {
        expect(screen.getByText('FY2024.zip')).toBeInTheDocument()
      })
    })

    it('refreshes history after successful upload', async () => {
      axiosInstance.post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
      })

      const mockHistoryAfterUpload = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          original_filename: 'new.zip',
          file: 'https://example.com/new.zip',
        },
      ]

      axiosInstance.get
        .mockResolvedValueOnce({ data: { results: [] } })
        .mockResolvedValue({ data: { results: mockHistoryAfterUpload } })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('No data available.')).toBeInTheDocument()
      })

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByText('new.zip')).toBeInTheDocument()
      })
    })
  })

  describe('Date Formatting', () => {
    it('formats timestamps correctly', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          status: 'SUCCEEDED',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        // Check that dates are formatted
        const dates = screen.getAllByText(/03\/05\/2025/)
        expect(dates.length).toBeGreaterThan(0)
      })
    })

    it('displays N/A for missing timestamps', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'PENDING',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        const cells = screen.getAllByText('N/A')
        expect(cells.length).toBeGreaterThan(0)
      })
    })
  })

  describe('Form Reset', () => {
    it('clears form after successful upload', async () => {
      axiosInstance.post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
      })

      renderComponent()

      await selectFiscalYear('2025')

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText(/Feedback report uploaded successfully/)
        ).toBeInTheDocument()
      })

      // Date should be cleared
      const dateInput = document.getElementById('date-extracted-on')
      expect(dateInput.value).toBe('')
    })

    it('resets form when fiscal year changes', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      setDateInputValue('2025-02-28')

      // Verify date was set
      const dateInput = document.getElementById('date-extracted-on')
      expect(dateInput.value).toBe('2025-02-28')

      // Change fiscal year
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2024' } })

      await waitFor(() => {
        expect(
          screen.getByText('Fiscal Year 2024 — Upload Feedback Reports')
        ).toBeInTheDocument()
      })

      // Date should be cleared (component re-rendered, get fresh reference)
      const newDateInput = document.getElementById('date-extracted-on')
      expect(newDateInput.value).toBe('')
    })
  })

  describe('Initialization', () => {
    it('calls fileInput.init() when fiscal year is selected', async () => {
      const { fileInput } = require('@uswds/uswds/src/js/components')

      renderComponent()

      // fileInput.init should not be called until fiscal year is selected
      // (FeedbackReportsUpload doesn't mount until year is selected)
      await selectFiscalYear('2025')

      expect(fileInput.init).toHaveBeenCalled()
    })
  })
})
