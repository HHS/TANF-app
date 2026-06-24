import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import AdminFeedbackReports from './AdminFeedbackReports'
import { get, post } from '../../fetch-instance'

jest.mock('../../fetch-instance')
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
          roles: [{ name: 'DIGIT Team' }],
        },
        authenticated: true,
      },
    })

    // Reset all mocks before each test
    jest.clearAllMocks()

    // Mock successful history fetch by default
    get.mockResolvedValue({
      data: { results: [] },
      ok: true,
      status: 200,
      error: null,
    })

    // Mock FileReader for async file handling
    global.FileReader = jest.fn().mockImplementation(() => ({
      readAsArrayBuffer: jest.fn(function () {
        setTimeout(() => this.onload && this.onload(), 0)
      }),
      result: new ArrayBuffer(8),
    }))
  })

  const renderComponent = (initialEntries = ['/feedback-reports']) => {
    return render(
      <MemoryRouter initialEntries={initialEntries}>
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
        screen.getByText(
          `Fiscal Year ${year} — Upload TANF/SSP Feedback Reports`
        )
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

    it('renders H2 header with selected fiscal year and report type', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      expect(
        screen.getByText('Fiscal Year 2025 — Upload TANF/SSP Feedback Reports')
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

  describe('Report Type Selection', () => {
    it('renders report type radio selector with TANF/SSP, Tribal TANF, and FRA options', () => {
      renderComponent()

      expect(screen.getByText('Feedback Report Type*')).toBeInTheDocument()
      expect(screen.getByLabelText('TANF/SSP')).toBeInTheDocument()
      expect(screen.getByLabelText('Tribal TANF')).toBeInTheDocument()
      expect(screen.getByLabelText('FRA')).toBeInTheDocument()
    })

    it('defaults to TANF/SSP report type', () => {
      renderComponent()

      const tanfRadio = screen.getByLabelText('TANF/SSP')
      expect(tanfRadio).toBeChecked()
    })

    it('updates header when FRA is selected', async () => {
      renderComponent()

      // Select FRA
      const fraRadio = screen.getByLabelText('FRA')
      fireEvent.click(fraRadio)

      // Select a year to see the header
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText('Fiscal Year 2025 — Upload FRA Feedback Reports')
        ).toBeInTheDocument()
      })
    })

    it('updates header when Tribal TANF is selected', async () => {
      renderComponent()

      const tribalTanfRadio = screen.getByLabelText('Tribal TANF')
      fireEvent.click(tribalTanfRadio)

      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(
            'Fiscal Year 2025 — Upload Tribal TANF Feedback Reports'
          )
        ).toBeInTheDocument()
      })
    })

    it('updates description text based on selected report type', () => {
      renderComponent()

      // Default TANF/SSP
      expect(
        screen.getByText(/TANF\/SSP submission history pages/)
      ).toBeInTheDocument()

      // Switch to FRA
      const fraRadio = screen.getByLabelText('FRA')
      fireEvent.click(fraRadio)

      expect(
        screen.getByText(/FRA submission history pages/)
      ).toBeInTheDocument()

      // Switch to Tribal TANF
      const tribalTanfRadio = screen.getByLabelText('Tribal TANF')
      fireEvent.click(tribalTanfRadio)

      expect(
        screen.getByText(/Tribal TANF submission history pages/)
      ).toBeInTheDocument()
      expect(screen.getByText(/each STT/)).toBeInTheDocument()
    })

    it('resets form state when report type changes', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      setDateInputValue('2025-02-28')

      // Change report type
      const fraRadio = screen.getByLabelText('FRA')
      fireEvent.click(fraRadio)

      // Date should be cleared
      const dateInput = document.getElementById('date-extracted-on')
      expect(dateInput.value).toBe('')
    })

    it('fetches history with report_type when type changes', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      // Clear mock calls from initial fetch
      get.mockClear()

      // Switch to FRA
      const fraRadio = screen.getByLabelText('FRA')
      fireEvent.click(fraRadio)

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/report-sources/'),
          expect.objectContaining({
            params: { year: '2025', report_type: 'FRA' },
          })
        )
      })
    })

    it('fetches history with TRIBAL_TANF when Tribal TANF is selected', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      get.mockClear()

      const tribalTanfRadio = screen.getByLabelText('Tribal TANF')
      fireEvent.click(tribalTanfRadio)

      await waitFor(() => {
        expect(get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/report-sources/'),
          expect.objectContaining({
            params: { year: '2025', report_type: 'TRIBAL_TANF' },
          })
        )
      })
    })

    it('includes report_type in upload POST', async () => {
      post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      // Select FRA
      const fraRadio = screen.getByLabelText('FRA')
      fireEvent.click(fraRadio)

      // Select year
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText('Fiscal Year 2025 — Upload FRA Feedback Reports')
        ).toBeInTheDocument()
      })

      await selectFile('FY2025.zip')
      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(post).toHaveBeenCalled()
        const formData = post.mock.calls[0][1]
        expect(formData.get('report_type')).toBe('FRA')
      })
    })

    it('includes TRIBAL_TANF in upload POST when Tribal TANF is selected', async () => {
      post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      const tribalTanfRadio = screen.getByLabelText('Tribal TANF')
      fireEvent.click(tribalTanfRadio)

      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '2025' } })

      await waitFor(() => {
        expect(
          screen.getByText(
            'Fiscal Year 2025 — Upload Tribal TANF Feedback Reports'
          )
        ).toBeInTheDocument()
      })

      await selectFile('FY2025.zip')
      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(post).toHaveBeenCalled()
        const formData = post.mock.calls[0][1]
        expect(formData.get('report_type')).toBe('TRIBAL_TANF')
      })
    })

    it('initializes report type from URL param', () => {
      renderComponent(['/feedback-reports?type=FRA'])

      const fraRadio = screen.getByLabelText('FRA')
      expect(fraRadio).toBeChecked()
    })

    it('defaults to TANF_SSP for invalid URL type param', () => {
      renderComponent(['/feedback-reports?type=INVALID'])

      const tanfRadio = screen.getByLabelText('TANF/SSP')
      expect(tanfRadio).toBeChecked()
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
        name: /Upload & Notify STTs/i,
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
        name: /Upload & Notify STTs/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByText('No file selected.')).toBeInTheDocument()
      })
    })

    it('successfully uploads a file with date and shows success message', async () => {
      post.mockResolvedValue({
        data: {
          id: 1,
          status: 'PENDING',
          original_filename: 'FY2025.zip',
        },
        ok: true,
        status: 200,
        error: null,
      })

      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      await selectFiscalYear('2025')

      // Select a file and wait for it to be processed
      await selectFile('FY2025.zip')

      // Set date (using helper for uncontrolled input)
      setDateInputValue('2025-02-28')

      // Click upload
      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText(
            /Feedback report uploaded successfully! Processing has begun/
          )
        ).toBeInTheDocument()
      })

      // Verify POST was called with year, date, and report_type
      expect(post).toHaveBeenCalledWith(
        expect.stringContaining('/reports/report-sources/'),
        expect.any(FormData)
      )
      const formData = post.mock.calls[0][1]
      expect(formData.get('report_type')).toBe('TANF_SSP')
    })

    it('shows error message when upload fails', async () => {
      post.mockResolvedValue({
        data: {
          file: ['Invalid zip file structure'],
        },
        ok: false,
        status: 400,
        error: new Error('HTTP 400'),
      })

      renderComponent()

      await selectFiscalYear('2025')

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText('Invalid zip file structure')
        ).toBeInTheDocument()
      })
    })

    it('shows loading state during upload', async () => {
      post.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () => resolve({ data: null, ok: true, status: 200, error: null }),
              100
            )
          )
      )

      renderComponent()

      await selectFiscalYear('2025')

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
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
    it('fetches history with report_type when fiscal year is selected', async () => {
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

      get.mockResolvedValue({
        data: { results: mockHistory },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
        expect(screen.getByText('02/28/2025')).toBeInTheDocument()
      })

      expect(get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/report-sources/'),
        expect.objectContaining({
          params: { year: '2025', report_type: 'TANF_SSP' },
        })
      )
    })

    it('displays empty state when no history exists', async () => {
      get.mockResolvedValue({
        data: { results: [] },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('No data available.')).toBeInTheDocument()
      })
    })

    it('displays error alert when history fetch fails', async () => {
      get.mockResolvedValue({
        data: null,
        ok: false,
        status: 500,
        error: new Error('Failed to fetch'),
      })

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
      get.mockImplementation((url, config) => {
        const year = config?.params?.year
        if (year === '2025') {
          return Promise.resolve({
            data: { results: mockHistory2025 },
            ok: true,
            status: 200,
            error: null,
          })
        }
        if (year === '2024') {
          return Promise.resolve({
            data: { results: mockHistory2024 },
            ok: true,
            status: 200,
            error: null,
          })
        }
        return Promise.resolve({
          data: { results: [] },
          ok: true,
          status: 200,
          error: null,
        })
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
      post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
        ok: true,
        status: 200,
        error: null,
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

      get
        .mockResolvedValueOnce({
          data: { results: [] },
          ok: true,
          status: 200,
          error: null,
        })
        .mockResolvedValue({
          data: { results: mockHistoryAfterUpload },
          ok: true,
          status: 200,
          error: null,
        })

      renderComponent()

      await selectFiscalYear('2025')

      await waitFor(() => {
        expect(screen.getByText('No data available.')).toBeInTheDocument()
      })

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
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

      get.mockResolvedValue({
        data: { results: mockHistory },
        ok: true,
        status: 200,
        error: null,
      })

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

      get.mockResolvedValue({
        data: { results: mockHistory },
        ok: true,
        status: 200,
        error: null,
      })

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
      post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
        ok: true,
        status: 200,
        error: null,
      })

      renderComponent()

      await selectFiscalYear('2025')

      await selectFile('FY2025.zip')

      setDateInputValue('2025-02-28')

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
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
          screen.getByText(
            'Fiscal Year 2024 — Upload TANF/SSP Feedback Reports'
          )
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

  describe('URL Parameter Handling', () => {
    it('handles invalid year in URL (NaN)', async () => {
      renderComponent(['?year=invalid'])

      // Should default to no selection when year is invalid
      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toHaveValue('')
      })

      // Upload section should not be visible
      expect(screen.queryByText('Feedback Reports ZIP')).not.toBeInTheDocument()
    })

    it('handles year not in valid options', async () => {
      renderComponent(['?year=1900'])

      // Should default to no selection when year is not in options
      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toHaveValue('')
      })
    })

    it('clears URL param when year selection is cleared', async () => {
      renderComponent(['?year=2025&type=TANF_SSP'])

      await waitFor(() => {
        expect(screen.getByLabelText('Fiscal Year')).toHaveValue('2025')
      })

      // Clear the year selection
      const fiscalYearSelect = screen.getByLabelText('Fiscal Year')
      fireEvent.change(fiscalYearSelect, { target: { value: '' } })

      // Upload section should be hidden
      await waitFor(() => {
        expect(
          screen.queryByText('Feedback Reports ZIP')
        ).not.toBeInTheDocument()
      })
    })

    it('initializes both type and year from URL params', async () => {
      renderComponent(['?type=FRA&year=2025'])

      await waitFor(() => {
        expect(screen.getByLabelText('FRA')).toBeChecked()
        expect(screen.getByLabelText('Fiscal Year')).toHaveValue('2025')
        expect(
          screen.getByText('Fiscal Year 2025 — Upload FRA Feedback Reports')
        ).toBeInTheDocument()
      })
    })
  })

  describe('Date Input Blur Handling', () => {
    it('clears date error when valid date is entered on blur', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      // First, trigger error by submitting without date
      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify STTs/i,
      })
      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText(
            "Choose the date that the data you're uploading was extracted from the database."
          )
        ).toBeInTheDocument()
      })

      // Now set a date and blur - error should clear
      const dateInput = document.getElementById('date-extracted-on')
      dateInput.value = '2025-02-28'
      fireEvent.blur(dateInput)

      await waitFor(() => {
        expect(
          screen.queryByText(
            "Choose the date that the data you're uploading was extracted from the database."
          )
        ).not.toBeInTheDocument()
      })
    })
  })

  describe('File Input Instructions Cleanup', () => {
    it('removes display-block class from instructions element when valid file selected', async () => {
      renderComponent()

      await selectFiscalYear('2025')

      // Create mock instructions element that USWDS would create
      const fileInput = document.querySelector('input[type="file"]')
      const dropTarget = fileInput.parentNode
      const instructions = document.createElement('div')
      instructions.className = 'usa-file-input__instructions display-block'
      dropTarget.appendChild(instructions)
      dropTarget.classList.add('has-invalid-file')

      // Select a valid file
      const file = new File(['content'], 'FY2025.zip', {
        type: 'application/zip',
      })
      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(instructions.classList.contains('display-block')).toBe(false)
        expect(dropTarget.classList.contains('has-invalid-file')).toBe(false)
      })
    })
  })
})
