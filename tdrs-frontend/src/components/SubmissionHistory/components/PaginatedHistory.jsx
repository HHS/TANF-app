import { useState, useEffect } from 'react'
import Paginator from '../../Paginator'
import { Spinner } from '../../Spinner'

export const PaginatedHistory = ({
  caption,
  files,
  loading,
  reprocessedState,
  TableComponent,
}) => {
  const pageSize = 5
  const [resultsPage, setResultsPage] = useState(1)

  // Reset state to initial state if the files change
  useEffect(() => {
    setResultsPage(1)
  }, [files])

  const pages =
    files && files.length > pageSize ? Math.ceil(files.length / pageSize) : 1
  const pageStart = (resultsPage - 1) * pageSize
  const pageEnd = Math.min(files.length, pageStart + pageSize)

  return (
    <div
      className="submission-history-section usa-table-container--scrollable"
      style={{ maxWidth: '100%' }}
      tabIndex={0}
    >
      <table className="usa-table usa-table--striped">
        <caption>{caption}</caption>
        {loading ? (
          <>
            <Spinner visible={true} />
            <span className="margin-left-1">Loading submission history...</span>
          </>
        ) : files && files.length > 0 ? (
          <TableComponent
            files={files.slice(pageStart, pageEnd)}
            reprocessedState={reprocessedState}
          />
        ) : (
          <span>No data available.</span>
        )}
      </table>

      {pages > 1 && (
        <Paginator
          onChange={(page) => setResultsPage(page)}
          selected={resultsPage}
          pages={pages}
        />
      )}
    </div>
  )
}
