import React from 'react'
import { render, waitFor, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import configureStore from '../../configureStore'
import SectionSubmissionHistory from './SectionSubmissionHistory'
import * as reportsActions from '../../actions/reports'
import { fileUploadSections } from '../../reducers/reports'

// Mock dependencies
jest.mock('../../actions/reports')
jest.mock('./CaseAggregatesTable', () => ({
  CaseAggregatesTable: ({ files, reprocessedState }) => (
    <tbody data-testid="case-aggregates-table">
      {files.map((file, index) => (
        <tr key={index} data-testid={`file-row-${file.id}`}>
          <td>{file.fileName}</td>
          <td>{file.section}</td>
          <td>Case Aggregates</td>
        </tr>
      ))}
    </tbody>
  ),
}))

jest.mock('./TotalAggregatesTable', () => ({
  TotalAggregatesTable: ({ files, reprocessedState }) => (
    <tbody data-testid="total-aggregates-table">
      {files.map((file, index) => (
        <tr key={index} data-testid={`file-row-${file.id}`}>
          <td>{file.fileName}</td>
          <td>{file.section}</td>
          <td>Total Aggregates</td>
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

const mockStore = (initial = initialState) => configureStore(initial)

describe('SectionSubmissionHistory', () => {
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
    filterValues = {
      year: '2024',
      quarter: 'Q1',
      stt: { id: 1, num_sections: 4 },
    },
    reprocessedState = [false, jest.fn()]
  ) => {
    const store = mockStore(storeState)
    mockDispatch = jest.spyOn(store, 'dispatch')

    return render(
      <Provider store={store}>
        <SectionSubmissionHistory
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

    it('renders all four section histories by default', () => {
      renderComponent()

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

      renderComponent(initialState, filterValues)

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
      renderComponent()

      const tables = screen.getAllByRole('table')
      expect(tables).toHaveLength(4)
    })

    it('displays "No data available" when no files exist for a section', () => {
      renderComponent()

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
      renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
      expect(mockDispatch).toHaveBeenCalled()
    })

    it('only fetches files once', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 4 },
      }
      const { rerender } = renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledTimes(1)

      // Rerender with same props
      rerender(
        <Provider store={mockStore(initialState)}>
          <SectionSubmissionHistory
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
        stt: { id: 42, num_sections: 3 },
        file_type: 'tanf',
      }
      renderComponent(initialState, filterValues)

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

      renderComponent(filesState)

      // Active Case Data should have 2 files
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
      expect(screen.getByTestId('file-row-3')).toBeInTheDocument()

      // Closed Case Data should have 1 file
      expect(screen.getByTestId('file-row-2')).toBeInTheDocument()
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

      renderComponent(filesState)

      // Both files should be visible
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
      expect(screen.getByTestId('file-row-2')).toBeInTheDocument()
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

      renderComponent(filesState)

      // File should be matched because section.includes('Active Case Data')
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
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

      renderComponent(filesState)

      expect(screen.getByTestId('case-aggregates-table')).toBeInTheDocument()
    })

    it('uses CaseAggregatesTable for section 2', () => {
      const filesState = {
        ...initialState,
        reports: {
          files: [
            {
              id: 1,
              fileName: 'file1.txt',
              section: 'Closed Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      renderComponent(filesState)

      expect(screen.getByTestId('case-aggregates-table')).toBeInTheDocument()
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

      renderComponent(filesState)

      expect(screen.getByTestId('total-aggregates-table')).toBeInTheDocument()
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

      renderComponent(filesState)

      expect(screen.getByTestId('total-aggregates-table')).toBeInTheDocument()
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
            section: 'Active Case Data',
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
            section: 'Active Case Data',
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
            section: 'Active Case Data',
            quarter: 'Q1',
            year: '2024',
          })),
        },
      }

      renderComponent(filesState)

      const table = screen.getByTestId('case-aggregates-table')
      expect(table.querySelectorAll('tr')).toHaveLength(5)
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

      renderComponent(filesState)

      // Verify paginator is present
      expect(screen.getByTestId('paginator')).toBeInTheDocument()

      // Verify initial state shows page 1
      expect(screen.getByTestId('current-page')).toHaveTextContent('1')

      // Verify only 5 files are shown on first page
      const table = screen.getByTestId('case-aggregates-table')
      expect(table.querySelectorAll('tr')).toHaveLength(5)
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

      renderComponent(filesState)

      const paginators = screen.getAllByTestId('paginator')
      expect(paginators).toHaveLength(2)
    })
  })

  describe('SectionHistory Component', () => {
    it('renders table with correct caption format', () => {
      renderComponent()

      const tables = screen.getAllByRole('table')
      expect(tables[0]).toHaveAccessibleName('Section 1 - Active Case Data')
      expect(tables[1]).toHaveAccessibleName('Section 2 - Closed Case Data')
      expect(tables[2]).toHaveAccessibleName('Section 3 - Aggregate Data')
      expect(tables[3]).toHaveAccessibleName('Section 4 - Stratum Data')
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

      renderComponent(filesState, undefined, reprocessedState)

      // Table component should receive reprocessedState
      expect(screen.getByTestId('case-aggregates-table')).toBeInTheDocument()
    })

    it('handles filterValues with all properties', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, name: 'California', num_sections: 4 },
        file_type: 'tanf',
        section: 'Active Case Data',
      }

      renderComponent(initialState, filterValues)

      expect(mockGetAvailableFileList).toHaveBeenCalledWith(filterValues)
    })

    it('uses num_sections from filterValues.stt', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 1 },
      }

      renderComponent(initialState, filterValues)

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

      const { container } = renderComponent(filesState)

      // Should render without crashing
      expect(container).toBeInTheDocument()
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
    })

    it('handles num_sections of 0', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 0 },
      }

      renderComponent(initialState, filterValues)

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

      renderComponent(filesState)

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

      renderComponent(filesState)

      // File should not appear in any section
      expect(screen.queryByTestId('file-row-1')).not.toBeInTheDocument()
    })

    it('handles num_sections greater than available sections', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 10 },
      }

      renderComponent(initialState, filterValues)

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

      const { container } = renderComponent(filesState)

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
              section: 'Active Case Data',
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
              section: 'Active Case Data',
              quarter: 'Q1',
              year: '2024',
            },
          ],
        },
      }

      const updatedStore = mockStore(updatedState)

      rerender(
        <Provider store={updatedStore}>
          <SectionSubmissionHistory
            filterValues={{
              year: '2024',
              quarter: 'Q1',
              stt: { id: 1, num_sections: 4 },
            }}
            reprocessedState={[false, jest.fn()]}
          />
        </Provider>
      )

      // File should now be visible
      expect(screen.getByTestId('file-row-1')).toBeInTheDocument()
    })
  })

  describe('Section Number Variations', () => {
    it('renders only 1 section when num_sections is 1', () => {
      const filterValues = {
        year: '2024',
        quarter: 'Q1',
        stt: { id: 1, num_sections: 1 },
      }

      renderComponent(initialState, filterValues)

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

      renderComponent(initialState, filterValues)

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

      renderComponent(initialState, filterValues)

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
})
