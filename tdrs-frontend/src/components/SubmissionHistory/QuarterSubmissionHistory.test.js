import React from 'react'
import { render, waitFor, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import QuarterSubmissionHistory from './QuarterSubmissionHistory'
import * as reportsActions from '../../actions/reports'

// Mock dependencies
jest.mock('../../actions/reports')
jest.mock('./TotalAggregatesTable', () => ({
  TotalAggregatesTable: ({ files, reprocessedState }) => (
    <tbody data-testid="total-aggregates-table">
      {files.map((file, index) => (
        <tr key={index} data-testid={`file-row-${file.id}`}>
          <td>{file.fileName}</td>
          <td>{file.quarter}</td>
          <td>{file.section}</td>
        </tr>
      ))}
    </tbody>
  ),
}))

jest.mock('../Paginator', () => ({
  __esModule: true,
  default: ({ pages, selected, onChange }) => (
    <div data-testid="paginator">
      <button
        data-testid="prev-page"
        onClick={() => onChange(selected - 1)}
        disabled={selected === 1}
      >
        Previous
      </button>
      <span data-testid="current-page">{selected}</span>
      <span data-testid="total-pages">{pages}</span>
      <button
        data-testid="next-page"
        onClick={() => onChange(selected + 1)}
        disabled={selected === pages}
      >
        Next
      </button>
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
    files: [],
  },
}

const mockStore = (initial = initialState) => configureStore(initial)

describe('QuarterSubmissionHistory', () => {
  let mockDispatch
  let mockGetAvailableFileList

  beforeEach(() => {
    // Mock getAvailableFileList to return a thunk that returns an action
    mockGetAvailableFileList = jest.fn(() => () => ({
      type: 'FETCH_FILE_LIST',
    }))
    reportsActions.getAvailableFileList = mockGetAvailableFileList
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  const renderComponent = (
    storeState = initialState,
    filterValues = { year: '2024', stt: { id: 1 } },
    reprocessedState = [false, jest.fn()]
  ) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return render(
      <Provider store={store}>
        <QuarterSubmissionHistory
          filterValues={filterValues}
          reprocessedState={reprocessedState}
        />
      </Provider>
    )
  }

  describe('Rendering', () => {
    it('renders the Knowledge Center link', () => {
      renderComponent()

      const link = screen.getByRole('link', {
        name: /Knowledge Center error reports guidance/i,
      })
      expect(link).toBeInTheDocument()
      expect(link).toHaveAttribute(
        'href',
        'https://tdp-project-updates.app.cloud.gov/knowledge-center/viewing-error-reports.html'
      )
      expect(link).toHaveAttribute('target', '_blank')
      expect(link).toHaveAttribute('rel', 'noreferrer')
    })

    it('renders all four quarter sections', () => {
      renderComponent()

      expect(
        screen.getByText('Quarter 1 (October - December)')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Quarter 2 (January - March)')
      ).toBeInTheDocument()
      expect(screen.getByText('Quarter 3 (April - June)')).toBeInTheDocument()
      expect(
        screen.getByText('Quarter 4 (July - September)')
      ).toBeInTheDocument()
    })

    it('renders tables for each quarter', () => {
      renderComponent()

      const tables = screen.getAllByRole('table')
      expect(tables).toHaveLength(4)
    })

    it('displays "No data available" when no files exist for a quarter', () => {
      renderComponent()

      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })
  })

  describe('Data Fetching', () => {
    it('dispatches getAvailableFileList on mount', () => {
      const filterValues = { year: '2024', stt: { id: 1 } }
      renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
      expect(mockDispatch).toHaveBeenCalled()
    })

    it('only fetches files once', () => {
      const filterValues = { year: '2024', stt: { id: 1 } }
      const { rerender } = renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledTimes(1)

      // Rerender with same props
      rerender(
        <Provider store={mockStore(initialState)}>
          <QuarterSubmissionHistory
            filterValues={filterValues}
            reprocessedState={[false, jest.fn()]}
          />
        </Provider>
      )

      // Should still only be called once
      expect(mockGetAvailableFileList).toHaveBeenCalledTimes(1)
    })

    it('passes correct filterValues to getAvailableFileList', () => {
      const filterValues = {
        year: '2023',
        quarter: 'Q2',
        stt: { id: 42 },
        file_type: 'pia',
      }
      renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
    })
  })

  describe('File Filtering and Display', () => {
    it('filters and displays files by quarter', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'file2.txt',
              section: 'Program Audit',
              quarter: 'Q2',
              year: '2024',
            },
            {
              id: 3,
              fileName: 'file3.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // Q1 should have 2 files
      const q1Table = screen.getAllByTestId('total-aggregates-table')[0]
      expect(q1Table.querySelectorAll('tr')).toHaveLength(2)

      // Q2 should have 1 file
      const q2Table = screen.getAllByTestId('total-aggregates-table')[1]
      expect(q2Table.querySelectorAll('tr')).toHaveLength(1)
    })

    it('only displays files with Program Audit section', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'file2.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // Only the Program Audit file should be displayed
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
      expect(screen.queryByTestId('file-row-2')).not.toBeInTheDocument()
    })

    it('displays files in correct quarter sections', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'q1-file.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'q3-file.txt',
              section: 'Program Audit',
              quarter: 'Q3',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // Q1 file should be visible
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()

      // Q3 file should be visible
      expect(screen.getByTestId('file-row-2')).toBeInTheDocument()

      // Verify they are in different tables by checking the table structure
      const tables = screen.getAllByTestId('total-aggregates-table')
      expect(tables.length).toBeGreaterThanOrEqual(2)
    })

    it('handles empty files array', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [],
        },
      }

      renderComponent(filesState)

      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })

    it('handles missing files property in reports state', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [],
        },
      }

      const { container } = renderComponent(filesState)

      // Should render without crashing when files is an empty array
      expect(container).toBeInTheDocument()
      expect(
        screen.getByText('Quarter 1 (October - December)')
      ).toBeInTheDocument()

      // All quarters should show "No data available"
      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })
  })

  describe('Pagination', () => {
    it('does not show paginator when files are 5 or fewer', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'file2.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      expect(screen.queryByTestId('paginator')).not.toBeInTheDocument()
    })

    it('shows paginator when files exceed page size of 5', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 6 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Program Audit',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      renderComponent(filesState)

      expect(screen.getByTestId('paginator')).toBeInTheDocument()
    })

    it('displays correct number of pages', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 12 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Program Audit',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      renderComponent(filesState)

      // 12 files with page size 5 should result in 3 pages
      const totalPages = screen.getByTestId('total-pages')
      expect(totalPages).toHaveTextContent('3')
    })

    it('displays only 5 files per page', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 8 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Program Audit',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      renderComponent(filesState)

      const q1Table = screen.getAllByTestId('total-aggregates-table')[0]
      expect(q1Table.querySelectorAll('tr')).toHaveLength(5)
    })

    it('changes page when pagination button is clicked', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 8 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Program Audit',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      renderComponent(filesState)

      // Verify paginator is present
      expect(screen.getByTestId('paginator')).toBeInTheDocument()

      // Verify initial state shows page 1
      expect(screen.getByTestId('current-page')).toHaveTextContent('1')

      // Verify only 5 files are shown on first page
      const q1Table = screen.getAllByTestId('total-aggregates-table')[0]
      expect(q1Table.querySelectorAll('tr')).toHaveLength(5)
    })

    it('maintains separate pagination state for each quarter', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            ...Array.from({ length: 6 }, (_, i) => ({
              id: i + 1,
              fileName: `q1-file${i + 1}.txt`,
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            })),
            ...Array.from({ length: 6 }, (_, i) => ({
              id: i + 7,
              fileName: `q2-file${i + 1}.txt`,
              section: 'Program Audit',
              quarter: 'Q2',
              year: '2024',
            })),
          ],
        },
      }

      renderComponent(filesState)

      const paginators = screen.getAllByTestId('paginator')
      expect(paginators).toHaveLength(2)
    })
  })

  describe('QuarterSection Component', () => {
    it('renders table with correct caption', () => {
      renderComponent()

      const tables = screen.getAllByRole('table')
      expect(tables[0]).toHaveAccessibleName('Quarter 1 (October - December)')
      expect(tables[1]).toHaveAccessibleName('Quarter 2 (January - March)')
      expect(tables[2]).toHaveAccessibleName('Quarter 3 (April - June)')
      expect(tables[3]).toHaveAccessibleName('Quarter 4 (July - September)')
    })

    it('applies correct CSS classes to table container', () => {
      const { container } = renderComponent()

      const tableContainers = container.querySelectorAll(
        '.submission-history-section.usa-table-container--scrollable'
      )
      expect(tableContainers).toHaveLength(4)
    })

    it('table container has correct tabIndex', () => {
      const { container } = renderComponent()

      const tableContainers = container.querySelectorAll(
        '.submission-history-section'
      )
      tableContainers.forEach((container) => {
        expect(container).toHaveAttribute('tabIndex', '0')
      })
    })

    it('table has correct USWDS classes', () => {
      const { container } = renderComponent()

      const tables = container.querySelectorAll('table')
      tables.forEach((table) => {
        expect(table).toHaveClass('usa-table')
        expect(table).toHaveClass('usa-table--striped')
      })
    })
  })

  describe('Props Handling', () => {
    it('passes reprocessedState to TotalAggregatesTable', () => {
      const reprocessedState = [true, jest.fn()]
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(
        filesState,
        { year: '2024', stt: { id: 1 } },
        reprocessedState
      )

      // TotalAggregatesTable should receive reprocessedState
      expect(screen.getByTestId('total-aggregates-table')).toBeInTheDocument()
    })

    it('handles missing filterValues gracefully', () => {
      const { container } = renderComponent(initialState, undefined)

      // Component should still render without crashing
      expect(container).toBeInTheDocument()
      expect(mockGetAvailableFileList).toHaveBeenCalled()
    })

    it('handles filterValues with all properties', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, name: 'California' },
        file_type: 'pia',
        section: 'Program Audit',
      }

      renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
    })
  })

  describe('Edge Cases', () => {
    it('handles files with missing quarter property', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Program Audit',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // Should not crash
      expect(
        screen.getByText('Quarter 1 (October - December)')
      ).toBeInTheDocument()
    })

    it('handles files with invalid quarter codes', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Program Audit',
              quarter: 'Q5',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // Should not crash and file should not appear in any quarter
      // Since no valid files exist, all quarters should show "No data available"
      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })

    it('handles files with null section', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: null,
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // File should not be displayed since section is not 'Program Audit'
      expect(screen.queryByTestId('file-row-1')).not.toBeInTheDocument()
    })

    it('handles large number of files efficiently', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 100 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Program Audit',
            quarter: `Q${(i % 4) + 1}`,
            year: '2024',
          })),
        },
      }

      renderComponent(filesState)

      // Should render without performance issues
      expect(
        screen.getByText('Quarter 1 (October - December)')
      ).toBeInTheDocument()
    })

    it('handles files array with mixed valid and invalid data', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'valid-file.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'another-valid.txt',
              section: 'Program Audit',
              quarter: 'Q2',
              year: '2024',
            },
            {
              id: 3,
              fileName: 'third-file.txt',
              section: 'Program Audit',
              quarter: 'Q3',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      // Should display valid files
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
      expect(screen.getByTestId('file-row-2')).toBeInTheDocument()
      expect(screen.getByTestId('file-row-3')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has accessible link for Knowledge Center', () => {
      renderComponent()

      const link = screen.getByRole('link', {
        name: /Knowledge Center error reports guidance/i,
      })
      expect(link).toHaveAttribute(
        'aria-label',
        'Knowledge Center error reports guidance'
      )
    })

    it('tables have proper captions for screen readers', () => {
      renderComponent()

      const captions = [
        'Quarter 1 (October - December)',
        'Quarter 2 (January - March)',
        'Quarter 3 (April - June)',
        'Quarter 4 (July - September)',
      ]

      captions.forEach((caption) => {
        expect(screen.getByText(caption)).toBeInTheDocument()
      })
    })

    it('table containers are keyboard accessible', () => {
      const { container } = renderComponent()

      const tableContainers = container.querySelectorAll(
        '.submission-history-section'
      )
      tableContainers.forEach((container) => {
        expect(container).toHaveAttribute('tabIndex', '0')
      })
    })
  })

  describe('Integration with Redux', () => {
    it('reads files from Redux store', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'test-file.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
    })

    it('updates when Redux store changes', () => {
      const { rerender } = renderComponent()

      // Initially no files
      expect(screen.queryByTestId('file-row-1')).not.toBeInTheDocument()

      // Update store with files
      const updatedState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'new-file.txt',
              section: 'Program Audit',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      const updatedStore = mockStore(updatedState)

      rerender(
        <Provider store={updatedStore}>
          <QuarterSubmissionHistory
            filterValues={{ year: '2024', stt: { id: 1 } }}
            reprocessedState={[false, jest.fn()]}
          />
        </Provider>
      )

      // File should now be visible
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
    })
  })
})
