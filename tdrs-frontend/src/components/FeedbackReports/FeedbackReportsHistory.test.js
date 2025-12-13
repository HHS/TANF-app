import React from 'react'
import { render, screen } from '@testing-library/react'
import FeedbackReportsHistory from './FeedbackReportsHistory'

describe('FeedbackReportsHistory', () => {
  let mockFormatDateTime

  beforeEach(() => {
    mockFormatDateTime = jest.fn((timestamp) => {
      if (!timestamp) return 'N/A'
      return new Date(timestamp).toLocaleString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true,
      })
    })
  })

  const renderComponent = (props = {}) => {
    const defaultProps = {
      data: [],
      formatDateTime: mockFormatDateTime,
    }
    return render(<FeedbackReportsHistory {...defaultProps} {...props} />)
  }

  describe('Empty State', () => {
    it('shows empty state when data is empty array', () => {
      renderComponent({ data: [] })

      expect(screen.getByText('No data available.')).toBeInTheDocument()
    })

    it('shows table with caption when empty', () => {
      renderComponent({ data: [] })

      expect(screen.getByRole('table')).toBeInTheDocument()
      expect(screen.getByText('Upload History')).toBeInTheDocument()
    })

    it('does not show table headers when empty', () => {
      renderComponent({ data: [] })

      expect(screen.queryByText('Fiscal year')).not.toBeInTheDocument()
    })
  })

  describe('Table Rendering', () => {
    const mockData = [
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

    it('renders table when data has entries', () => {
      renderComponent({ data: mockData })

      expect(screen.getByRole('table')).toBeInTheDocument()
    })

    it('renders table caption', () => {
      renderComponent({ data: mockData })

      expect(screen.getByText('Upload History')).toBeInTheDocument()
    })

    it('renders all table headers', () => {
      renderComponent({ data: mockData })

      expect(screen.getByText('Fiscal year')).toBeInTheDocument()
      expect(screen.getByText('Feedback uploaded on')).toBeInTheDocument()
      expect(screen.getByText('Notifications sent on')).toBeInTheDocument()
      expect(screen.getByText('Status')).toBeInTheDocument()
      expect(screen.getByText('Error')).toBeInTheDocument()
      expect(screen.getByText('File')).toBeInTheDocument()
    })

    it('applies correct table classes', () => {
      const { container } = renderComponent({
        data: mockData,
      })

      const table = container.querySelector('table')
      expect(table).toHaveClass('usa-table')
      expect(table).toHaveClass('usa-table--striped')
    })
  })

  describe('Data Display', () => {
    it('renders report data correctly', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(screen.getByText('2025')).toBeInTheDocument()
      expect(screen.getByText('FY2025.zip')).toBeInTheDocument()
    })

    it('calls formatDateTime for created_at', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(mockFormatDateTime).toHaveBeenCalledWith('2025-03-05T10:31:00Z')
    })

    it('calls formatDateTime for processed_at', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(mockFormatDateTime).toHaveBeenCalledWith('2025-03-05T10:41:00Z')
    })

    it('shows current year when report.year is null', () => {
      const currentYear = new Date().getFullYear()
      const mockData = [
        {
          id: 1,
          year: null,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(screen.getByText(currentYear.toString())).toBeInTheDocument()
    })

    it('shows report.year when it exists', () => {
      const mockData = [
        {
          id: 1,
          year: 2024,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(screen.getByText('2024')).toBeInTheDocument()
    })
  })

  describe('Download Links', () => {
    it('renders download link when original_filename exists', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025.zip',
          file: 'https://example.com/FY2025.zip',
        },
      ]

      renderComponent({ data: mockData })

      const link = screen.getByText('FY2025.zip')
      expect(link).toBeInTheDocument()
      expect(link.tagName).toBe('A')
      expect(link).toHaveAttribute('href', 'https://example.com/FY2025.zip')
      expect(link).toHaveAttribute('download', 'FY2025.zip')
      expect(link).toHaveClass('usa-link')
    })

    it('shows N/A when original_filename is null', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: null,
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      // File column should show N/A for null filename
      expect(screen.getByText('N/A')).toBeInTheDocument()
    })

    it('shows N/A when original_filename is empty string', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: '',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      // File column should show N/A for empty filename
      expect(screen.getByText('N/A')).toBeInTheDocument()
    })
  })

  describe('Multiple Records', () => {
    it('renders multiple records correctly', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'FY2025_Q1.zip',
          file: 'https://example.com/FY2025_Q1.zip',
        },
        {
          id: 2,
          year: 2025,
          created_at: '2025-01-08T09:41:00Z',
          processed_at: '2025-01-08T09:48:00Z',
          original_filename: 'FY2025_Q2.zip',
          file: 'https://example.com/FY2025_Q2.zip',
        },
        {
          id: 3,
          year: 2024,
          created_at: '2024-12-15T14:20:00Z',
          processed_at: '2024-12-15T14:30:00Z',
          original_filename: 'FY2024_Q4.zip',
          file: 'https://example.com/FY2024_Q4.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(screen.getByText('FY2025_Q1.zip')).toBeInTheDocument()
      expect(screen.getByText('FY2025_Q2.zip')).toBeInTheDocument()
      expect(screen.getByText('FY2024_Q4.zip')).toBeInTheDocument()
    })

    it('each row has unique key (report.id)', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test1.zip',
          file: 'https://example.com/test1.zip',
        },
        {
          id: 2,
          year: 2025,
          created_at: '2025-01-08T09:41:00Z',
          processed_at: '2025-01-08T09:48:00Z',
          original_filename: 'test2.zip',
          file: 'https://example.com/test2.zip',
        },
      ]

      const { container } = renderComponent({
        data: mockData,
      })

      const rows = container.querySelectorAll('tbody tr')
      expect(rows).toHaveLength(2)
    })
  })

  describe('Edge Cases', () => {
    it('handles null processed_at timestamp', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(mockFormatDateTime).toHaveBeenCalledWith(null)
      // formatDateTime returns 'N/A' for null, which gets rendered in the td
      const naCells = screen.getAllByText('N/A')
      expect(naCells.length).toBeGreaterThan(0)
    })

    it('handles missing file URL', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          original_filename: 'test.zip',
          file: null,
        },
      ]

      renderComponent({ data: mockData })

      // Should still render the filename link even if file URL is null
      // (or show N/A if original_filename is falsy)
      expect(screen.getByText('test.zip')).toBeInTheDocument()
    })
  })

  describe('Status Display', () => {
    it('displays status value in table', () => {
      const mockData = [
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

      renderComponent({ data: mockData })

      expect(screen.getByText('SUCCEEDED')).toBeInTheDocument()
    })

    it('renders clock icon for PENDING status', () => {
      const mockData = [
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

      const { container } = renderComponent({ data: mockData })

      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveAttribute('data-icon', 'clock')
      expect(icon).toHaveAttribute('color', '#005EA2')
    })

    it('renders clock icon for PROCESSING status', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'PROCESSING',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      const { container } = renderComponent({ data: mockData })

      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveAttribute('data-icon', 'clock')
      expect(icon).toHaveAttribute('color', '#005EA2')
    })

    it('renders check-circle icon for SUCCEEDED status', () => {
      const mockData = [
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

      const { container } = renderComponent({ data: mockData })

      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveAttribute('data-icon', 'circle-check')
      expect(icon).toHaveAttribute('color', '#40bb45')
    })

    it('renders xmark-circle icon for FAILED status', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'FAILED',
          error_message: 'Something went wrong',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      const { container } = renderComponent({ data: mockData })

      const icon = container.querySelector('svg')
      expect(icon).toBeInTheDocument()
      expect(icon).toHaveAttribute('data-icon', 'circle-xmark')
      expect(icon).toHaveAttribute('color', '#bb0000')
    })

    it('renders no icon for unknown status', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'UNKNOWN_STATUS',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      const { container } = renderComponent({ data: mockData })

      const icon = container.querySelector('svg')
      expect(icon).not.toBeInTheDocument()
    })

    it('icon has margin-right-1 class', () => {
      const mockData = [
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

      const { container } = renderComponent({ data: mockData })

      const icon = container.querySelector('svg')
      expect(icon).toHaveClass('margin-right-1')
    })

    it('displays error message when present', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: null,
          status: 'FAILED',
          error_message: 'Invalid ZIP structure',
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(screen.getByText('FAILED')).toBeInTheDocument()
      expect(screen.getByText('Invalid ZIP structure')).toBeInTheDocument()
    })

    it('displays "None" when no error message', () => {
      const mockData = [
        {
          id: 1,
          year: 2025,
          created_at: '2025-03-05T10:31:00Z',
          processed_at: '2025-03-05T10:41:00Z',
          status: 'SUCCEEDED',
          error_message: null,
          original_filename: 'test.zip',
          file: 'https://example.com/test.zip',
        },
      ]

      renderComponent({ data: mockData })

      expect(screen.getByText('SUCCEEDED')).toBeInTheDocument()
      expect(screen.getByText('None')).toBeInTheDocument()
    })
  })
})
