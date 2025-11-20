import React from 'react'
import { Provider } from 'react-redux'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import configureStore from 'redux-mock-store'
import { thunk } from 'redux-thunk'
import FeedbackReports from './FeedbackReports'
import axiosInstance from '../../axios-instance'

jest.mock('../../axios-instance')

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
    axiosInstance.get.mockResolvedValue({ data: [] })
  })

  const renderComponent = () => {
    return render(
      <Provider store={store}>
        <FeedbackReports />
      </Provider>
    )
  }

  describe('Component Rendering', () => {
    it('renders the page title and subtitle', async () => {
      renderComponent()

      expect(screen.getByText('Upload Feedback Reports')).toBeInTheDocument()
      expect(
        screen.getByText(
          'TANF WPR, SSP WPR, TANF & SSP Combined, and Time Limit Reports'
        )
      ).toBeInTheDocument()
    })

    it('renders the file upload section', () => {
      renderComponent()

      expect(screen.getByText('Feedback Reports ZIP')).toBeInTheDocument()
      expect(screen.getByText(/Drag file here or/)).toBeInTheDocument()
      expect(screen.getByText(/choose from folder/)).toBeInTheDocument()
      expect(screen.getByText('Only .zip files are accepted')).toBeInTheDocument()
    })

    it('renders the upload button', () => {
      renderComponent()

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      expect(uploadButton).toBeInTheDocument()
      expect(uploadButton).toBeDisabled() // Should be disabled without file
    })

    it('renders the upload history section', () => {
      renderComponent()

      expect(screen.getByText('Upload History')).toBeInTheDocument()
    })

    it('renders the info alert about notification distribution', () => {
      renderComponent()

      expect(
        screen.getByText(/Once submitted, TDP will distribute feedback reports/)
      ).toBeInTheDocument()
    })
  })

  describe('File Upload Functionality', () => {
    it('enables upload button when a valid .zip file is selected', async () => {
      renderComponent()

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })

      await waitFor(() => {
        expect(uploadButton).not.toBeDisabled()
      })
    })

    it('shows error when non-.zip file is selected', async () => {
      renderComponent()

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.txt', { type: 'text/plain' })

      fireEvent.change(fileInput, { target: { files: [file] } })

      await waitFor(() => {
        expect(screen.getByText('File must be a zip folder')).toBeInTheDocument()
      })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })
      expect(uploadButton).toBeDisabled()
    })

    it('successfully uploads a file and shows success message', async () => {
      axiosInstance.post.mockResolvedValue({
        data: {
          id: 1,
          status: 'PENDING',
          original_filename: 'feedback.zip',
        },
      })

      axiosInstance.get.mockResolvedValue({ data: [] })

      renderComponent()

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

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

      expect(axiosInstance.post).toHaveBeenCalledWith(
        expect.stringContaining('/v1/reports/report-sources/'),
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

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

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

    it('shows generic error message when upload fails without specific error', async () => {
      axiosInstance.post.mockRejectedValue(new Error('Network error'))

      renderComponent()

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
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

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

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
    it('fetches and displays upload history on mount', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          status: 'SUCCEEDED',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: mockHistory })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('2025')).toBeInTheDocument()
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
        expect(screen.getByText('Complete')).toBeInTheDocument()
      })

      expect(axiosInstance.get).toHaveBeenCalledWith(
        expect.stringContaining('/v1/reports/report-sources/'),
        expect.objectContaining({ withCredentials: true })
      )
    })

    it('displays empty state when no history exists', async () => {
      axiosInstance.get.mockResolvedValue({ data: [] })

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText('No feedback reports uploaded yet')
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
          screen.getByText('Failed to load upload history. Please refresh the page.')
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
          status: 'SUCCEEDED',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
        {
          id: 2,
          year: 2025,
          created_at: '2025-01-08T09:41:00Z',
          processed_at: '2025-01-08T09:48:00Z',
          status: 'SUCCEEDED',
          original_filename: 'FY2025_Q1.zip',
          file: 'https://example.com/FY2025_Q1.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: mockHistory })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
        expect(screen.getByText('FY2025_Q1.zip')).toBeInTheDocument()
        expect(screen.getByText('Showing 2 uploads')).toBeInTheDocument()
      })
    })

    it('displays different status badges correctly', async () => {
      const mockHistory = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'PENDING',
          original_filename: 'pending.zip',
          file: 'https://example.com/pending.zip',
        },
        {
          id: 2,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'PROCESSING',
          original_filename: 'processing.zip',
          file: 'https://example.com/processing.zip',
        },
        {
          id: 3,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          status: 'SUCCEEDED',
          original_filename: 'succeeded.zip',
          file: 'https://example.com/succeeded.zip',
        },
        {
          id: 4,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          status: 'FAILED',
          original_filename: 'failed.zip',
          file: 'https://example.com/failed.zip',
        },
      ]

      axiosInstance.get.mockResolvedValue({ data: mockHistory })

      renderComponent()

      await waitFor(() => {
        expect(screen.getByText('Pending')).toBeInTheDocument()
        expect(screen.getByText('Processing')).toBeInTheDocument()
        expect(screen.getByText('Complete')).toBeInTheDocument()
        expect(screen.getByText('Failed')).toBeInTheDocument()
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
          status: 'PENDING',
          original_filename: 'new.zip',
          file: 'https://example.com/new.zip',
        },
      ]

      axiosInstance.get
        .mockResolvedValueOnce({ data: [] }) // Initial fetch
        .mockResolvedValueOnce({ data: mockHistory }) // After upload

      renderComponent()

      await waitFor(() => {
        expect(
          screen.getByText('No feedback reports uploaded yet')
        ).toBeInTheDocument()
      })

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(screen.getByText('new.zip')).toBeInTheDocument()
      })

      // Should have called GET twice: once on mount, once after upload
      expect(axiosInstance.get).toHaveBeenCalledTimes(2)
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

      axiosInstance.get.mockResolvedValue({ data: mockHistory })

      renderComponent()

      await waitFor(() => {
        // Check that dates are formatted (exact format may vary by locale)
        expect(screen.getByText(/03\/05\/2025/)).toBeInTheDocument()
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

      axiosInstance.get.mockResolvedValue({ data: mockHistory })

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

      const fileInput = screen.getByLabelText(/Drag file here or/i)
      const file = new File(['content'], 'feedback.zip', {
        type: 'application/zip',
      })

      fireEvent.change(fileInput, { target: { files: [file] } })

      const uploadButton = screen.getByRole('button', {
        name: /Upload & Notify States/i,
      })

      fireEvent.click(uploadButton)

      await waitFor(() => {
        expect(uploadButton).toBeDisabled()
      })
    })
  })
})
