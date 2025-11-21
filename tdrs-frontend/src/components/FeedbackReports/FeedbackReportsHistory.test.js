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
      uploadHistory: [],
      isLoading: false,
      formatDateTime: mockFormatDateTime,
    }
    return render(<FeedbackReportsHistory {...defaultProps} {...props} />)
  }

  describe('Loading State', () => {
    it('shows loading state when isLoading is true', () => {
      renderComponent({ isLoading: true })

      expect(screen.getByText('Loading upload history...')).toBeInTheDocument()
    })

    it('shows loading text with correct classes', () => {
      const { container } = renderComponent({ isLoading: true })

      const loadingDiv = container.querySelector('.padding-y-3.text-center')
      expect(loadingDiv).toBeInTheDocument()
    })

    it('does not show table when loading', () => {
      renderComponent({ isLoading: true })

      expect(screen.queryByRole('table')).not.toBeInTheDocument()
    })

    it('does not show empty state when loading', () => {
      renderComponent({ isLoading: true })

      expect(
        screen.queryByText('No feedback reports uploaded yet')
      ).not.toBeInTheDocument()
    })
  })

  describe('Empty State', () => {
    it('shows empty state when uploadHistory is empty array', () => {
      renderComponent({ uploadHistory: [], isLoading: false })

      expect(
        screen.getByText('No feedback reports uploaded yet')
      ).toBeInTheDocument()
    })

    it('shows empty state with correct styling classes', () => {
      const { container } = renderComponent({
        uploadHistory: [],
        isLoading: false,
      })

      const emptyDiv = container.querySelector(
        '.padding-y-3.text-center.border-1px.border-base-lighter.radius-md'
      )
      expect(emptyDiv).toBeInTheDocument()
    })

    it('does not show table when empty', () => {
      renderComponent({ uploadHistory: [], isLoading: false })

      expect(screen.queryByRole('table')).not.toBeInTheDocument()
    })
  })

  describe('Table Rendering', () => {
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

    it('renders table when uploadHistory has data', () => {
      renderComponent({ uploadHistory: mockData, isLoading: false })

      expect(screen.getByRole('table')).toBeInTheDocument()
    })

    it('renders table caption', () => {
      renderComponent({ uploadHistory: mockData, isLoading: false })

      expect(screen.getByText('Upload History')).toBeInTheDocument()
    })

    it('renders all table headers', () => {
      renderComponent({ uploadHistory: mockData, isLoading: false })

      expect(screen.getByText('Fiscal year')).toBeInTheDocument()
      expect(screen.getByText('Feedback uploaded on')).toBeInTheDocument()
      expect(screen.getByText('Notifications sent on')).toBeInTheDocument()
      expect(screen.getByText('File')).toBeInTheDocument()
    })

    it('applies correct table classes', () => {
      const { container } = renderComponent({
        uploadHistory: mockData,
        isLoading: false,
      })

      const table = container.querySelector('table')
      expect(table).toHaveClass('usa-table')
      expect(table).toHaveClass('usa-table--striped')
      expect(table).toHaveClass('margin-top-4')
      expect(table).toHaveClass('desktop:width-tablet')
      expect(table).toHaveClass('mobile:width-full')
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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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
        uploadHistory: mockData,
        isLoading: false,
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

      renderComponent({ uploadHistory: mockData, isLoading: false })

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

      renderComponent({ uploadHistory: mockData, isLoading: false })

      // Should still render the filename link even if file URL is null
      // (or show N/A if original_filename is falsy)
      expect(screen.getByText('test.zip')).toBeInTheDocument()
    })
  })
})
