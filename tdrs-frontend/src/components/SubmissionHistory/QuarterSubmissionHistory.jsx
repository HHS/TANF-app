import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Paginator from '../Paginator'
import { getAvailableFileList } from '../../actions/reports'
import {
  programIntegrityAuditLabels,
} from '../Reports/utils'
import { CaseAggregatesTable } from './CaseAggregatesTable'

const QuarterSection = ({ label, files, reprocessedState }) => {
  const pageSize = 5
  const [resultsPage, setResultsPage] = useState(1)

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
        <caption>{label}</caption>
        {files && files.length > 0 ? (
          <CaseAggregatesTable
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

const QuarterSubmissionHistory = ({ filterValues, reprocessedState }) => {
  const dispatch = useDispatch()
  const [hasFetchedFiles, setHasFetchedFiles] = useState(false)
  const { files } = useSelector((state) => state.reports)

  useEffect(() => {
    if (!hasFetchedFiles) {
      dispatch(getAvailableFileList({ ...filterValues, quarter: null }))
      setHasFetchedFiles(true)
    }
  }, [hasFetchedFiles, files, dispatch, filterValues])

  return (
    <>
      <div className="margin-top-2 margin-bottom-5">
        <a
          className="usa-link"
          href="https://tdp-project-updates.app.cloud.gov/knowledge-center/viewing-error-reports.html"
          target="_blank"
          aria-label="Knowledge Center error reports guidance"
          rel="noreferrer"
        >
          Visit the Knowledge Center for further guidance on reviewing error
          reports
        </a>
      </div>
      <div>
        {programIntegrityAuditLabels.map((quarterLabel, index) => {
          const quarterCode = `Q${index + 1}`
          const filteredFiles = files.filter(
            (f) =>
              f.quarter === quarterCode
          )

          return (
            <QuarterSection
              key={quarterLabel}
              label={quarterLabel}
              files={filteredFiles}
              reprocessedState={reprocessedState}
            />
          )
        })}
      </div>
    </>
  )
}

export default QuarterSubmissionHistory
