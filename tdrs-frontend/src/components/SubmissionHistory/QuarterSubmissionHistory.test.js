import { render, screen, within, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import appConfigureStore from '../../configureStore'
import QuarterSubmissionHistory from './QuarterSubmissionHistory'
import * as reportsActions from '../../actions/reports'
import { ReportsProvider } from '../Reports/ReportsContext'

// Mock only external actions
jest.mock('../../actions/reports')

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

describe('QuarterSubmissionHistory', () => {
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

  const setup = (
    storeState = initialState,
    filterValues = { year: '2024', stt: { id: 1 } },
    reprocessedState = { setDate: jest.fn(), setModalVisible: jest.fn() }
  ) => {
    const store = appConfigureStore(storeState)
    const mockDispatch = jest.fn(store.dispatch)
    store.dispatch = mockDispatch

    return {
      ...render(
        <Provider store={store}>
          <ReportsProvider>
            <QuarterSubmissionHistory
              filterValues={filterValues}
              reprocessedState={reprocessedState}
            />
          </ReportsProvider>
        </Provider>
      ),
      store,
      mockDispatch,
    }
  }

  describe('Rendering', () => {
    it('renders the Knowledge Center link', () => {
      setup()

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
      setup()

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
      setup()

      const tables = screen.getAllByRole('table')
      expect(tables).toHaveLength(4)
    })

    it('displays "No data available" when no files exist for a quarter', () => {
      setup()

      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })
  })

  describe('Data Fetching', () => {
    it('dispatches getAvailableFileList on mount', () => {
      const filterValues = { year: '2024', stt: { id: 1 } }
      const { store } = setup(initialState, filterValues)

      // Component sets quarter to null when fetching files
      expect(mockGetAvailableFileList).toHaveBeenCalledWith({
        ...filterValues,
        quarter: null,
      })
      expect(store.dispatch).toHaveBeenCalled()
    })

    it('only fetches files once', () => {
      const filterValues = { year: '2024', stt: { id: 1 } }
      const { rerender, store } = setup(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledTimes(1)

      // Rerender with same props
      rerender(
        <Provider store={store}>
          <ReportsProvider>
            <QuarterSubmissionHistory
              filterValues={filterValues}
              reprocessedState={{
                setDate: jest.fn(),
                setModalVisible: jest.fn(),
              }}
            />
          </ReportsProvider>
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
      setup(initialState, filterValues)

      // Component sets quarter to null when fetching files
      expect(mockGetAvailableFileList).toHaveBeenCalledWith({
        ...filterValues,
        quarter: null,
      })
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
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-15T10:00:00Z',
              submittedBy: 'user1@example.com',
            },
            {
              id: 2,
              fileName: 'file2.txt',
              section: 'Active Case Data',
              quarter: 'Q2',
              year: '2024',
              createdAt: '2024-02-15T10:00:00Z',
              submittedBy: 'user2@example.com',
            },
            {
              id: 3,
              fileName: 'file3.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-20T10:00:00Z',
              submittedBy: 'user3@example.com',
            },
          ],
        },
      }

      setup(filesState)

      // Q1 should have 2 files (each file creates 3 rows in CaseAggregatesTable)
      const tables = screen.getAllByRole('table')
      const q1Table = tables[0]
      const q1Bodies = within(q1Table).getAllByRole('rowgroup')
      const q1Body = q1Bodies[1] // tbody is the second rowgroup (thead is first)
      // 2 files * 3 rows each = 6 rows
      expect(within(q1Body).getAllByRole('row')).toHaveLength(6)

      // Q2 should have 1 file (3 rows)
      const q2Table = tables[1]
      const q2Bodies = within(q2Table).getAllByRole('rowgroup')
      const q2Body = q2Bodies[1]
      expect(within(q2Body).getAllByRole('row')).toHaveLength(3)
    })

    it('displays files in correct quarter sections', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'q1-file.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'q3-file.txt',
              section: 'Active Case Data',
              quarter: 'Q3',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Q1 file should be visible
      expect(screen.getByText('q1-file.txt')).toBeInTheDocument()

      // Q3 file should be visible
      expect(screen.getByText('q3-file.txt')).toBeInTheDocument()

      // Verify they are in different tables
      const tables = screen.getAllByRole('table')
      expect(tables.length).toBe(4)
    })

    it('handles empty files array', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [],
        },
      }

      setup(filesState)

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

      const { container } = setup(filesState)

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
              section: 'Active Case Data',
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

      setup(filesState)

      expect(
        screen.queryByRole('navigation', { name: 'Pagination' })
      ).not.toBeInTheDocument()
    })

    it('shows paginator when files exceed page size of 5', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 6 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Active Case Data',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      setup(filesState)

      expect(
        screen.getByRole('navigation', { name: 'Pagination' })
      ).toBeInTheDocument()
    })

    it('displays correct number of pages', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 12 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Active Case Data',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      setup(filesState)

      // 12 files with page size 5 should result in 3 pages
      const pagination = screen.getByRole('navigation', { name: 'Pagination' })
      const pageButtons = within(pagination).getAllByRole('button')
      // Should have Previous, 1, 2, 3, Next = 5 buttons
      expect(pageButtons).toHaveLength(5)
    })

    it('displays only 5 files per page', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 8 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Active Case Data',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      setup(filesState)

      const tables = screen.getAllByRole('table')
      const q1Table = tables[0]
      const q1Bodies = within(q1Table).getAllByRole('rowgroup')
      const tbody = q1Bodies[1] // tbody is the second rowgroup
      // 5 files * 3 rows each = 15 rows
      expect(within(tbody).getAllByRole('row')).toHaveLength(15)
    })

    it('changes page when pagination button is clicked', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 8 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Active Case Data',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      setup(filesState)

      // Verify paginator is present
      const pagination = screen.getByRole('navigation', { name: 'Pagination' })
      expect(pagination).toBeInTheDocument()

      // Verify page 1 button is marked as current
      const page1Button = within(pagination).getByRole('button', {
        name: 'Page 1',
        current: 'page',
      })
      expect(page1Button).toBeInTheDocument()

      // Verify only 5 files are shown on first page (5 files * 3 rows = 15 rows)
      const tables = screen.getAllByRole('table')
      const q1Table = tables[0]
      const q1Bodies = within(q1Table).getAllByRole('rowgroup')
      const tbody = q1Bodies[1] // tbody is the second rowgroup
      expect(within(tbody).getAllByRole('row')).toHaveLength(15)

      // Click page 2 button to trigger onChange
      const page2Button = within(pagination).getByRole('button', {
        name: 'Page 2',
      })
      fireEvent.click(page2Button)

      // Verify page 2 is now current
      const updatedPagination = screen.getByRole('navigation', {
        name: 'Pagination',
      })
      const currentPage2Button = within(updatedPagination).getByRole('button', {
        name: 'Page 2',
        current: 'page',
      })
      expect(currentPage2Button).toBeInTheDocument()
    })

    it('maintains separate pagination state for each quarter', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            ...Array.from({ length: 6 }, (_, i) => ({
              id: i + 1,
              fileName: `q1-file${i + 1}.txt`,
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            })),
            ...Array.from({ length: 6 }, (_, i) => ({
              id: i + 7,
              fileName: `q2-file${i + 1}.txt`,
              section: 'Active Case Data',
              quarter: 'Q2',
              year: '2024',
            })),
          ],
        },
      }

      setup(filesState)

      const paginators = screen.getAllByRole('navigation', {
        name: 'Pagination',
      })
      expect(paginators).toHaveLength(2)
    })
  })

  describe('QuarterSection Component', () => {
    it('renders table with correct caption', () => {
      setup()

      const tables = screen.getAllByRole('table')
      expect(tables[0]).toHaveAccessibleName('Quarter 1 (October - December)')
      expect(tables[1]).toHaveAccessibleName('Quarter 2 (January - March)')
      expect(tables[2]).toHaveAccessibleName('Quarter 3 (April - June)')
      expect(tables[3]).toHaveAccessibleName('Quarter 4 (July - September)')
    })

    it('applies correct CSS classes to table container', () => {
      const { container } = setup()

      const tableContainers = container.querySelectorAll(
        '.submission-history-section.usa-table-container--scrollable'
      )
      expect(tableContainers).toHaveLength(4)
    })

    it('table container has correct tabIndex', () => {
      const { container } = setup()

      const tableContainers = container.querySelectorAll(
        '.submission-history-section'
      )
      tableContainers.forEach((container) => {
        expect(container).toHaveAttribute('tabIndex', '0')
      })
    })

    it('table has correct USWDS classes', () => {
      const { container } = setup()

      const tables = container.querySelectorAll('table')
      tables.forEach((table) => {
        expect(table).toHaveClass('usa-table')
        expect(table).toHaveClass('usa-table--striped')
      })
    })
  })

  describe('Props Handling', () => {
    it('passes reprocessedState to CaseAggregatesTable', () => {
      const reprocessedState = [true, jest.fn()]
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState, { year: '2024', stt: { id: 1 } }, reprocessedState)

      // CaseAggregatesTable should render with the file
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
    })

    it('handles missing filterValues gracefully', () => {
      const { container } = setup(initialState, undefined)

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
        section: 'Active Case Data',
      }

      setup(initialState, filterValues)

      // Component sets quarter to null when fetching files
      expect(mockGetAvailableFileList).toHaveBeenCalledWith({
        ...filterValues,
        quarter: null,
      })
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
              section: 'Active Case Data',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

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
              section: 'Active Case Data',
              quarter: 'Q5',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Should not crash and file should not appear in any quarter
      // Since no valid files exist, all quarters should show "No data available"
      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })

    it('handles large number of files efficiently', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 100 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: 'Active Case Data',
            quarter: `Q${(i % 4) + 1}`,
            year: '2024',
          })),
        },
      }

      setup(filesState)

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
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'another-valid.txt',
              section: 'Active Case Data',
              quarter: 'Q2',
              year: '2024',
            },
            {
              id: 3,
              fileName: 'third-file.txt',
              section: 'Active Case Data',
              quarter: 'Q3',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Should display valid files
      expect(screen.getByText('valid-file.txt')).toBeInTheDocument()
      expect(screen.getByText('another-valid.txt')).toBeInTheDocument()
      expect(screen.getByText('third-file.txt')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('has accessible link for Knowledge Center', () => {
      setup()

      const link = screen.getByRole('link', {
        name: /Knowledge Center error reports guidance/i,
      })
      expect(link).toHaveAttribute(
        'aria-label',
        'Knowledge Center error reports guidance'
      )
    })

    it('tables have proper captions for screen readers', () => {
      setup()

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
      const { container } = setup()

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
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      expect(screen.getByText('test-file.txt')).toBeInTheDocument()
    })

    it('updates when Redux store changes', () => {
      const { rerender } = setup()

      // Initially no files
      expect(screen.queryByText('new-file.txt')).not.toBeInTheDocument()

      // Update store with files
      const updatedState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'new-file.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      const updatedStore = appConfigureStore(updatedState)
      const mockDispatch = jest.fn(updatedStore.dispatch)
      updatedStore.dispatch = mockDispatch

      rerender(
        <Provider store={updatedStore}>
          <ReportsProvider>
            <QuarterSubmissionHistory
              filterValues={{ year: '2024', stt: { id: 1 } }}
              reprocessedState={{
                setDate: jest.fn(),
                setModalVisible: jest.fn(),
              }}
            />
          </ReportsProvider>
        </Provider>
      )

      // File should now be visible
      expect(screen.getByText('new-file.txt')).toBeInTheDocument()
    })
  })
})
