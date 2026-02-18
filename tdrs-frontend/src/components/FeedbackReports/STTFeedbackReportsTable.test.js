import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import STTFeedbackReportsTable from './STTFeedbackReportsTable'
import axiosInstance from '../../axios-instance'
import { downloadBlob } from '../../utils/fileDownload'

jest.mock('../../axios-instance')
jest.mock('../../utils/fileDownload')

describe('STTFeedbackReportsTable', () => {
  const mockSetAlert = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  afterEach(() => {
    jest.restoreAllMocks()
  })

  const renderComponent = (data = []) => {
    return render(
      <STTFeedbackReportsTable data={data} setAlert={mockSetAlert} />
    )
  }

  describe('Empty State', () => {
    it('displays empty message when no data', () => {
      renderComponent([])

      expect(
        screen.getByText('No feedback reports available for this fiscal year.')
      ).toBeInTheDocument()
    })

    it('displays empty message when data is undefined', () => {
      render(
        <STTFeedbackReportsTable data={undefined} setAlert={mockSetAlert} />
      )

      expect(
        screen.getByText('No feedback reports available for this fiscal year.')
      ).toBeInTheDocument()
    })
  })

  describe('Table Rendering', () => {
    it('renders table headers when data exists', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('Generated on')).toBeInTheDocument()
      expect(
        screen.getByText('Reflects data submitted through')
      ).toBeInTheDocument()
      expect(screen.getByText('Files')).toBeInTheDocument()
    })

    it('renders report data correctly with formatted date_extracted_on', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('F33.zip')).toBeInTheDocument()
      expect(screen.getByText('02/28/2025')).toBeInTheDocument()
    })

    it('renders multiple reports', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-03-31',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'report1.zip',
        },
        {
          id: 2,
          date_extracted_on: '2025-01-31',
          created_at: '2025-01-08T09:48:00Z',
          original_filename: 'report2.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('report1.zip')).toBeInTheDocument()
      expect(screen.getByText('report2.zip')).toBeInTheDocument()
      expect(screen.getByText('03/31/2025')).toBeInTheDocument()
      expect(screen.getByText('01/31/2025')).toBeInTheDocument()
    })
  })

  describe('Date Formatting', () => {
    it('formats timestamps correctly', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      // Check that date is formatted (locale-specific format)
      const dates = screen.getAllByText(/03\/05\/2025/i)
      expect(dates.length).toBeGreaterThan(0)
    })

    it('displays N/A for missing timestamps', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: null,
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('N/A')).toBeInTheDocument()
    })

    it('displays N/A for missing date_extracted_on', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: null,
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      // Should have one N/A for the missing date_extracted_on
      expect(screen.getByText('N/A')).toBeInTheDocument()
    })

    it('formats date_extracted_on from YYYY-MM-DD to MM/DD/YYYY', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-12-25',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('12/25/2025')).toBeInTheDocument()
    })
  })

  describe('Download Functionality', () => {
    it('renders download button with filename', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', {
        name: /Download F33.zip/i,
      })
      expect(downloadButton).toBeInTheDocument()
    })

    it('renders default download text when filename is missing', () => {
      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: null,
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', { name: /Download/i })
      expect(downloadButton).toBeInTheDocument()
    })

    it('triggers download on click', async () => {
      const mockBlob = new Blob(['test content'], { type: 'application/zip' })
      axiosInstance.get.mockResolvedValue({ data: mockBlob })

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', {
        name: /Download F33.zip/i,
      })
      fireEvent.click(downloadButton)

      await waitFor(() => {
        expect(axiosInstance.get).toHaveBeenCalledWith(
          expect.stringContaining('/reports/1/download/'),
          expect.objectContaining({
            responseType: 'blob',
            withCredentials: true,
          })
        )
      })

      await waitFor(() => {
        expect(downloadBlob).toHaveBeenCalledWith(mockBlob, 'F33.zip')
      })
    })

    it('shows downloading state during download', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', {
        name: /Download F33.zip/i,
      })
      fireEvent.click(downloadButton)

      await waitFor(() => {
        expect(screen.getByText('Downloading...')).toBeInTheDocument()
      })
    })

    it('shows error alert when download fails', async () => {
      axiosInstance.get.mockRejectedValue(new Error('Download failed'))

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', {
        name: /Download F33.zip/i,
      })
      fireEvent.click(downloadButton)

      await waitFor(() => {
        expect(mockSetAlert).toHaveBeenCalledWith({
          active: true,
          type: 'error',
          message: 'Failed to download the report. Please try again.',
        })
      })
    })

    it('clears alert before starting download', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', {
        name: /Download F33.zip/i,
      })
      fireEvent.click(downloadButton)

      expect(mockSetAlert).toHaveBeenCalledWith({
        active: false,
        type: null,
        message: null,
      })
    })

    it('uses fallback filename "report.zip" when original_filename is missing', async () => {
      const mockBlob = new Blob(['test content'], { type: 'application/zip' })
      axiosInstance.get.mockResolvedValue({ data: mockBlob })

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: null,
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', { name: /Download/i })
      fireEvent.click(downloadButton)

      await waitFor(() => {
        expect(downloadBlob).toHaveBeenCalledWith(mockBlob, 'report.zip')
      })
    })

    it('disables button during download', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      const downloadButton = screen.getByRole('button', {
        name: /Download F33.zip/i,
      })
      fireEvent.click(downloadButton)

      await waitFor(() => {
        const disabledButton = screen.getByRole('button', {
          name: /Download/i,
        })
        expect(disabledButton).toHaveAttribute('disabled')
      })
    })
  })

  describe('Multiple Downloads', () => {
    it('only disables the downloading button, not others', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const mockData = [
        {
          id: 1,
          date_extracted_on: '2025-02-28',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'report1.zip',
        },
        {
          id: 2,
          date_extracted_on: '2025-03-31',
          created_at: '2025-03-06T10:41:00Z',
          original_filename: 'report2.zip',
        },
      ]

      renderComponent(mockData)

      const firstDownloadButton = screen.getByRole('button', {
        name: /Download report1.zip/i,
      })
      fireEvent.click(firstDownloadButton)

      await waitFor(() => {
        // First button should be disabled/downloading
        expect(screen.getByText('Downloading...')).toBeInTheDocument()
        // Second button should still be clickable
        const secondButton = screen.getByRole('button', {
          name: /Download report2.zip/i,
        })
        expect(secondButton).not.toHaveAttribute('disabled')
      })
    })
  })
})
