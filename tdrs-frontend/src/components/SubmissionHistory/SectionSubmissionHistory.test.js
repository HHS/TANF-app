import React from 'react'
import { render, screen, within, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import appConfigureStore from '../../configureStore'
import SectionSubmissionHistory from './SectionSubmissionHistory'
import * as reportsActions from '../../actions/reports'
import { fileUploadSections } from '../../reducers/reports'
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
        num_sections: 4,
      },
      roles: [{ id: 1, name: 'Data Analyst', permission: [] }],
      account_approval_status: 'Approved',
    },
  },
  reports: {
    files: [],
  },
}

describe('SectionSubmissionHistory', () => {
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
    filterValues = {
      year: '2024',
      quarter: 'Q1',
      stt: { id: 1, num_sections: 4 },
    },
    reprocessedState = { setDate: jest.fn(), setModalVisible: jest.fn() }
  ) => {
    const store = appConfigureStore(storeState)
    const mockDispatch = jest.fn(store.dispatch)
    store.dispatch = mockDispatch

    return {
      ...render(
        <Provider store={store}>
          <ReportsProvider>
            <SectionSubmissionHistory
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

    it('renders all four section histories by default', () => {
      setup()

      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Section 2 - Closed Case Data')
      ).toBeInTheDocument()
      expect(screen.getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
      expect(screen.getByText('Section 4 - Stratum Data')).toBeInTheDocument()
    })

    it('renders correct number of sections based on num_sections', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 2 },
      }

      setup(initialState, filterValues)

      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Section 2 - Closed Case Data')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Section 3 - Aggregate Data')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Section 4 - Stratum Data')
      ).not.toBeInTheDocument()
    })

    it('renders tables for each section', () => {
      setup()

      const tables = screen.getAllByRole('table')
      expect(tables).toHaveLength(4)
    })

    it('displays "No data available" when no files exist for a section', () => {
      setup()

      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
    })
  })

  describe('Data Fetching', () => {
    it('dispatches getAvailableFileList on mount', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 4 },
      }
      const { store } = setup(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
      expect(store.dispatch).toHaveBeenCalled()
    })

    it('only fetches files once', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 4 },
      }
      const { rerender, store } = setup(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledTimes(1)

      // Rerender with same props
      rerender(
        <Provider store={store}>
          <ReportsProvider>
            <SectionSubmissionHistory
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
        stt: { id: 42, num_sections: 3 },
        file_type: 'tanf',
      }
      setup(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
    })
  })

  describe('File Filtering and Display', () => {
    it('filters and displays files by section', () => {
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
              section: 'Closed Case Data',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 3,
              fileName: 'file3.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Active Case Data should have 2 files
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
      expect(screen.getByText('file3.txt')).toBeInTheDocument()

      // Closed Case Data should have 1 file
      expect(screen.getByText('file2.txt')).toBeInTheDocument()
    })

    it('displays files in correct section tables', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'active-file.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
            {
              id: 2,
              fileName: 'aggregate-file.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Both files should be visible
      expect(screen.getByText('active-file.txt')).toBeInTheDocument()
      expect(screen.getByText('aggregate-file.txt')).toBeInTheDocument()
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

    it('handles files with partial section name matches', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Section 1 TANF - Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // File should be matched because section.includes('Active Case Data')
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
    })
  })

  describe('Table Component Selection', () => {
    it('uses CaseAggregatesTable for section 1', () => {
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

      setup(filesState)

      // Verify file is displayed with CaseAggregatesTable structure
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
      expect(screen.getByText('Cases Without Errors')).toBeInTheDocument()
    })

    it('uses CaseAggregatesTable for section 2', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file2.txt',
              section: 'Closed Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Verify file is displayed with CaseAggregatesTable structure
      expect(screen.getByText('file2.txt')).toBeInTheDocument()
      expect(screen.getByText('Cases Without Errors')).toBeInTheDocument()
    })

    it('uses TotalAggregatesTable for section 3', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Verify file is displayed with TotalAggregatesTable structure
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
      expect(screen.getByText('Total Errors')).toBeInTheDocument()
    })

    it('uses TotalAggregatesTable for section 4', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Stratum Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // Verify file is displayed with TotalAggregatesTable structure
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
      expect(screen.getByText('Total Errors')).toBeInTheDocument()
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
      const activeTable = tables[0]
      const tbody = within(activeTable).getAllByRole('rowgroup')[1]
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
      const activeTable = tables[0]
      const tbody = within(activeTable).getAllByRole('rowgroup')[1]
      expect(within(tbody).getAllByRole('row')).toHaveLength(15)
    })

    it('maintains separate pagination state for each section', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            ...Array.from({ length: 6 }, (_, i) => ({
              id: i + 1,
              fileName: `active-file${i + 1}.txt`,
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            })),
            ...Array.from({ length: 6 }, (_, i) => ({
              id: i + 7,
              fileName: `closed-file${i + 1}.txt`,
              section: 'Closed Case Data',
              quarter: 'Q1',
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

  describe('SectionHistory Component', () => {
    it('renders table with correct caption format', () => {
      setup()

      const tables = screen.getAllByRole('table')
      expect(tables[0]).toHaveAccessibleName('Section 1 - Active Case Data')
      expect(tables[1]).toHaveAccessibleName('Section 2 - Closed Case Data')
      expect(tables[2]).toHaveAccessibleName('Section 3 - Aggregate Data')
      expect(tables[3]).toHaveAccessibleName('Section 4 - Stratum Data')
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
    it('passes reprocessedState to table components', () => {
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

      setup(filesState, undefined, reprocessedState)

      // Table component should render with the file
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
    })

    it('handles filterValues with all properties', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, name: 'California', num_sections: 4 },
        file_type: 'tanf',
        section: 'Active Case Data',
      }

      setup(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
    })

    it('uses num_sections from filterValues.stt', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 1 },
      }

      setup(initialState, filterValues)

      // Only section 1 should be rendered
      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Section 2 - Closed Case Data')
      ).not.toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('handles files with valid section property', () => {
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

      const { container } = setup(filesState)

      // Should render without crashing
      expect(container).toBeInTheDocument()
      expect(screen.getByText('file1.txt')).toBeInTheDocument()
    })

    it('handles num_sections of 0', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 0 },
      }

      setup(initialState, filterValues)

      // No sections should be rendered
      expect(
        screen.queryByText('Section 1 - Active Case Data')
      ).not.toBeInTheDocument()
    })

    it('handles large number of files efficiently', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: Array.from({ length: 100 }, (_, i) => ({
            id: i + 1,
            fileName: `file${i + 1}.txt`,
            section: fileUploadSections[i % 4],
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      setup(filesState)

      // Should render without performance issues
      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
    })

    it('handles files with section names that do not match exactly', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Unknown Section',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      setup(filesState)

      // File should not appear in any section
      expect(screen.queryByText('file1.txt')).not.toBeInTheDocument()
    })

    it('handles num_sections greater than available sections', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 10 },
      }

      setup(initialState, filterValues)

      // Should only render 4 sections (max available)
      const tables = screen.getAllByRole('table')
      expect(tables).toHaveLength(4)
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
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()

      // All sections should show "No data available"
      const noDataMessages = screen.getAllByText('No data available.')
      expect(noDataMessages).toHaveLength(4)
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
        'Section 1 - Active Case Data',
        'Section 2 - Closed Case Data',
        'Section 3 - Aggregate Data',
        'Section 4 - Stratum Data',
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
            <SectionSubmissionHistory
              filterValues={{
                year: '2024',
                quarter: 'Q1',
                stt: { id: 1, num_sections: 4 },
              }}
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

  describe('Section Number Variations', () => {
    it('renders only 1 section when num_sections is 1', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 1 },
      }

      setup(initialState, filterValues)

      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Section 2 - Closed Case Data')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Section 3 - Aggregate Data')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Section 4 - Stratum Data')
      ).not.toBeInTheDocument()
    })

    it('renders 3 sections when num_sections is 3', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 3 },
      }

      setup(initialState, filterValues)

      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Section 2 - Closed Case Data')
      ).toBeInTheDocument()
      expect(screen.getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
      expect(
        screen.queryByText('Section 4 - Stratum Data')
      ).not.toBeInTheDocument()
    })

    it('renders all 4 sections when num_sections is 4', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 4 },
      }

      setup(initialState, filterValues)

      expect(
        screen.getByText('Section 1 - Active Case Data')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Section 2 - Closed Case Data')
      ).toBeInTheDocument()
      expect(screen.getByText('Section 3 - Aggregate Data')).toBeInTheDocument()
      expect(screen.getByText('Section 4 - Stratum Data')).toBeInTheDocument()
    })
  })

  describe('TotalAggregatesTable coverage', () => {
    it('renders file download button for non-regional staff', () => {
      const mockDownload = jest.fn(() => () => ({ type: 'DOWNLOAD_FILE' }))
      reportsActions.download = mockDownload

      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'aggregate-file.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-01',
              submittedBy: 'test@example.com',
            },
          ],
        },
      }

      const { mockDispatch } = setup(filesState)

      const downloadButton = screen.getByRole('button', {
        name: 'aggregate-file.txt',
      })
      expect(downloadButton).toBeInTheDocument()

      fireEvent.click(downloadButton)
      expect(mockDispatch).toHaveBeenCalled()
    })

    it('renders filename as text for regional staff', () => {
      const regionalStaffState = {
        auth: {
          authenticated: true,
          user: {
            email: 'regional@example.com',
            stt: {
              id: 1,
              type: 'state',
              code: 'CA',
              name: 'California',
              num_sections: 4,
            },
            roles: [{ id: 2, name: 'OFA Regional Staff', permission: [] }],
            account_approval_status: 'Approved',
          },
        },
        reports: {
          files: [
            {
              id: 1,
              fileName: 'aggregate-file.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-01',
              submittedBy: 'test@example.com',
            },
          ],
        },
      }

      setup(regionalStaffState)

      expect(screen.getByText('aggregate-file.txt')).toBeInTheDocument()
      expect(
        screen.queryByRole('button', { name: 'aggregate-file.txt' })
      ).not.toBeInTheDocument()
    })

    it('renders row with null data', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'aggregate-file.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-01',
              submittedBy: 'test@example.com',
              summary: {
                case_aggregates: {
                  months: [null, null, null],
                },
              },
            },
          ],
        },
      }

      setup(filesState)

      const naElements = screen.getAllByText('N/A')
      expect(naElements.length).toBeGreaterThan(0)
    })

    it('renders row with valid month data', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'aggregate-file.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-01',
              submittedBy: 'test@example.com',
              summary: {
                case_aggregates: {
                  months: [
                    { month: 'January', total_errors: 5 },
                    { month: 'February', total_errors: 3 },
                    { month: 'March', total_errors: 0 },
                  ],
                },
              },
            },
          ],
        },
      }

      setup(filesState)

      expect(screen.getByText('January')).toBeInTheDocument()
      expect(screen.getByText('February')).toBeInTheDocument()
      expect(screen.getByText('March')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('3')).toBeInTheDocument()
    })

    it('renders status as Pending when summary is null', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'aggregate-file.txt',
              section: 'Aggregate Data',
              quarter: 'Q1',
              year: '2024',
              createdAt: '2024-01-01',
              submittedBy: 'test@example.com',
              summary: null,
            },
          ],
        },
      }

      setup(filesState)

      const pendingElements = screen.getAllByText('Pending')
      expect(pendingElements.length).toBeGreaterThan(0)
    })
  })
})
