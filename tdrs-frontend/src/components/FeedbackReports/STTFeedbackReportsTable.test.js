import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import STTFeedbackReportsTable from './STTFeedbackReportsTable'
import axiosInstance from '../../axios-instance'

jest.mock('../../axios-instance')

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
          quarter: 'Q1',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('Feedback generated on')).toBeInTheDocument()
      expect(
        screen.getByText('Fiscal quarters included in feedback')
      ).toBeInTheDocument()
      expect(screen.getByText('Files')).toBeInTheDocument()
    })

    it('renders report data correctly', () => {
      const mockData = [
        {
          id: 1,
          quarter: 'Q2',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('F33.zip')).toBeInTheDocument()
      expect(screen.getByText('Q2')).toBeInTheDocument()
    })

    it('renders multiple reports', () => {
      const mockData = [
        {
          id: 1,
          quarter: 'Q2',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'report1.zip',
        },
        {
          id: 2,
          quarter: 'Q1',
          created_at: '2025-01-08T09:48:00Z',
          original_filename: 'report2.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('report1.zip')).toBeInTheDocument()
      expect(screen.getByText('report2.zip')).toBeInTheDocument()
      expect(screen.getByText('Q1')).toBeInTheDocument()
      expect(screen.getByText('Q2')).toBeInTheDocument()
    })
  })

  describe('Date Formatting', () => {
    it('formats timestamps correctly', () => {
      const mockData = [
        {
          id: 1,
          quarter: 'Q1',
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
          quarter: 'Q1',
          created_at: null,
          original_filename: 'test.zip',
        },
      ]

      renderComponent(mockData)

      expect(screen.getByText('N/A')).toBeInTheDocument()
    })
  })

  describe('Download Functionality', () => {
    it('renders download button with filename', () => {
      const mockData = [
        {
          id: 1,
          quarter: 'Q1',
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
          quarter: 'Q1',
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

      // Mock URL.createObjectURL and revokeObjectURL
      const mockUrl = 'blob:http://localhost:3000/mock-blob-url'
      global.URL.createObjectURL = jest.fn(() => mockUrl)
      global.URL.revokeObjectURL = jest.fn()

      const mockData = [
        {
          id: 1,
          quarter: 'Q1',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'F33.zip',
        },
      ]

      // Render BEFORE mocking document.createElement
      renderComponent(mockData)

      // Mock document.createElement for the anchor element only after render
      const mockClick = jest.fn()
      const originalCreateElement = document.createElement.bind(document)
      jest.spyOn(document, 'createElement').mockImplementation((tagName) => {
        if (tagName === 'a') {
          return {
            href: '',
            setAttribute: jest.fn(),
            click: mockClick,
            style: {},
          }
        }
        return originalCreateElement(tagName)
      })
      jest.spyOn(document.body, 'appendChild').mockImplementation(() => {})
      jest.spyOn(document.body, 'removeChild').mockImplementation(() => {})

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

      // Cleanup mocks
      document.createElement.mockRestore()
      document.body.appendChild.mockRestore()
      document.body.removeChild.mockRestore()
    })

    it('shows downloading state during download', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const mockData = [
        {
          id: 1,
          quarter: 'Q1',
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
          quarter: 'Q1',
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
          quarter: 'Q1',
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

    it('disables button during download', async () => {
      axiosInstance.get.mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      )

      const mockData = [
        {
          id: 1,
          quarter: 'Q1',
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
          quarter: 'Q1',
          created_at: '2025-03-05T10:41:00Z',
          original_filename: 'report1.zip',
        },
        {
          id: 2,
          quarter: 'Q2',
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
