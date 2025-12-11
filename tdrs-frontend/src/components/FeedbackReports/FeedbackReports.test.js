import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import FeedbackReports from './FeedbackReports'
import axiosInstance from '../../axios-instance'

jest.mock('../../axios-instance')
jest.mock('../../utils/createFileInputErrorState')
jest.mock('@uswds/uswds/src/js/components', () => ({
  fileInput: {
    init: jest.fn(),
  },
}))

const mockStore = configureStore([thunk])

describe('FeedbackReports', () => {
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
          <FeedbackReports />
        </Provider>
      </MemoryRouter>
    )
  }

  describe('Component Rendering', () => {
    it('renders the page title and subtitle', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(/Once submitted, TDP will distribute/)
        ).toBeInTheDocument()
      })
    })

    it('renders the file upload section', async () => {
      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })
    })

    it('renders the upload button', async () => {
      renderComponent()

      await waitFor(() => {
        const uploadButton = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(uploadButton).toBeInTheDocument()
        expect(uploadButton).toHaveAttribute('disabled') // Should be disabled without file
      })
    })

    it('renders the upload history empty state initially', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText('No data available.')
        ).toBeInTheDocument()
      })
    })

    it('renders the info alert about notification distribution', async () => {
      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(
            /Once submitted, TDP will distribute feedback reports/
          )
        ).toBeInTheDocument()
      })
    })
  })

  describe('File Upload Functionality', () => {
    it('enables upload button when a valid .zip file is selected', async () => {
      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        const uploadButton = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(uploadButton).not.toHaveAttribute('disabled')
      })
    })

    it('shows error when non-.zip file is selected', async () => {
      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.txt', { type: 'text/plain' })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(screen.getByText('File must be a .zip file')).toBeInTheDocument()
      })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      expect(uploadButton).toHaveAttribute('disabled')
    })

    it('successfully uploads a file and shows success message', async () => {
      axiosInstance.post.mockResolvedValue({
        data: {
          id: 1,
          status: 'PENDING',
          original_filename: 'feedback.zip',
        },
      })

      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      // Wait for FileReader async process to complete and button to be enabled
      const uploadButton = await waitFor(() => {
        const btn = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(btn).not.toHaveAttribute('disabled')
        return btn
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText(
            /Feedback report uploaded successfully! Processing has begun/
          )
        ).toBeInTheDocument()
      })

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

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      // Wait for FileReader async process to complete and button to be enabled
      const uploadButton = await waitFor(() => {
        const btn = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(btn).not.toHaveAttribute('disabled')
        return btn
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText('Invalid zip file structure')
        ).toBeInTheDocument()
      })
    })

    it('shows generic error message when upload fails without specific error', async () => {
      axiosInstance.post.mockRejectedValue(new Error('Network error'))

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      // Wait for FileReader async process to complete and button to be enabled
      const uploadButton = await waitFor(() => {
        const btn = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(btn).not.toHaveAttribute('disabled')
        return btn
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(
          screen.getByText('Upload failed. Please try again.')
        ).toBeInTheDocument()
      })
    })

    it('shows loading state during upload', async () => {
      axiosInstance.post.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      // Wait for FileReader async process to complete and button to be enabled
      const uploadButton = await waitFor(() => {
        const btn = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(btn).not.toHaveAttribute('disabled')
        return btn
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
    it('fetches and displays upload history on mount', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('2025')).toBeInTheDocument()
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
      })

      expect(axiosInstance.get).toHaveBeenCalledWith(
        expect.stringContaining('/reports/report-sources/'),
        expect.objectContaining({ withCredentials: true })
      )
    })

    it('displays empty state when no history exists', async () => {
      axiosInstance.get.mockResolvedValue({ data: { results: [] } })

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText('No data available.')
        ).toBeInTheDocument()
      })
    })

    it('displays loading state while fetching history', () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      renderComponent()

      expect(screen.getByText('Loading upload history...')).toBeInTheDocument()
    })

    it('displays error alert when history fetch fails', async () => {
      axiosInstance.get.mockRejectedValue(new Error('Failed to fetch'))

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText(
            'Failed to load upload history. Please refresh the page.'
          )
        ).toBeInTheDocument()
      })
    })

    it('displays multiple history entries correctly', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
        {
          id: 2,
          year: 2025,
          created_at: '2025-01-08T09:41:00Z',
          processed_at: '2025-01-08T09:48:00Z',
          original_filename: 'FY2025_Q1.zip',
          file: 'https://example.com/FY2025_Q1.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
        expect(screen.getByText('FY2025_Q1.zip')).toBeInTheDocument()
      })
    })

    it('refreshes history after successful upload', async () => {
      axiosInstance.post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
      })

      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          original_filename: 'new.zip',
          file: 'https://example.com/new.zip',
        },
      ]

      // Initial fetch returns empty, all subsequent calls return mockHistory
      axiosInstance.get
        .mockResolvedValueOnce({ data: { results: [] } }) // Initial fetch
        .mockResolvedValue({ data: { results: mockHistory } }) // All subsequent calls (including after upload)

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText('No data available.')
        ).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      // Wait for FileReader async process to complete and button to be enabled
      const uploadButton = await waitFor(() => {
        const btn = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(btn).not.toHaveAttribute('disabled')
        return btn
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByText('new.zip')).toBeInTheDocument()
      })

      // Should have called GET at least twice: once on mount, once after upload
      expect(axiosInstance.get.mock.calls.length).toBeGreaterThanOrEqual(2)
    })
  })

  describe('Date Formatting', () => {
    it('formats timestamps correctly', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          status: 'SUCCEEDED',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await waitFor(() => {
        // Check that dates are formatted (exact format may vary by locale)
        const dates = screen.getAllByText(/03\/05\/2025/)
        expect(dates.length).toBeGreaterThan(0)
      })
    })

    it('displays N/A for missing timestamps', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'PENDING',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await waitFor(() => {
        const cells = screen.getAllByText('N/A')
        expect(cells.length).toBeGreaterThan(0)
      })
    })
  })

  describe('File Input Interaction', () => {
    it('clears file selection after successful upload', async () => {
      axiosInstance.post.mockResolvedValue({
        data: { id: 1, status: 'PENDING' },
      })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      })

      const fileInput = document.querySelector('input[type="file"]')
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      // Wait for FileReader async process to complete and button to be enabled
      const uploadButton = await waitFor(() => {
        const btn = screen.getByRole('button', {
          name: /Upload & Notify States/i,
        })
        expect(btn).not.toHaveAttribute('disabled')
        return btn
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(uploadButton).toHaveAttribute('disabled')
      })
    })
  })

  describe('Initialization', () => {
    it('calls fileInput.init() on mount', () => {
      const { fileInput } = require('@uswds/uswds/src/js/components')

      renderComponent()

      expect(fileInput.init).toHaveBeenCalled()
    })
  })

  describe('Paginated Response Handling', () => {
    it('handles paginated response with results array', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('test.zip')).toBeInTheDocument()
      })
    })

  })

  describe('Year Fallback', () => {
    it('displays current year when report year is null', async () => {
      const currentYear = new Date().getFullYear()
      const mockHistory = [
        {
          id: 1,
          year: null,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: { results: mockHistory } })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText(currentYear.toString())).toBeInTheDocument()
      })
    })
  })
})
