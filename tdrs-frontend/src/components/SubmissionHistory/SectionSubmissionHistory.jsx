import React, { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Paginator from '../Paginator'
import { getAvailableFileList } from '../../actions/reports'
import { fileUploadSections } from '../../reducers/reports'
import { CaseAggregatesTable } from './CaseAggregatesTable'
import { TotalAggregatesTable } from './TotalAggregatesTable'

const SectionHistory = ({ section, label, files, reprocessedState }) => {
  const pageSize = 5
  const [resultsPage, setResultsPage] = useState(1)

  const pages =
    files && files.length > pageSize ? Math.ceil(files.length / pageSize) : 1
  const pageStart = (resultsPage - 1) * pageSize
  const pageEnd = Math.min(files.length, pageStart + pageSize)

  const TableComponent =
    section === 1 || section === 2 ? CaseAggregatesTable : TotalAggregatesTable

  return (
    <div
      className="submission-history-section usa-table-container--scrollable"
      style={{ maxWidth: '100%' }}
      tabIndex={0}
    >
      <table className="usa-table usa-table--striped">
        <caption>{`Section ${section} - ${label}`}</caption>
        {files && files.length > 0 ? (
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

const SectionSubmissionHistory = ({ filterValues, reprocessedState }) => {
  const dispatch = useDispatch()
  const [hasFetchedFiles, setHasFetchedFiles] = useState(false)
  const { files } = useSelector((state) => state.reports)
  const num_sections = filterValues.stt.num_sections

  useEffect(() => {
    if (!hasFetchedFiles) {
      dispatch(getAvailableFileList(filterValues))
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
        {fileUploadSections.slice(0, num_sections).map((section, index) => {
          return (
            <SectionHistory
              key={section}
              section={index + 1}
              label={section}
              files={files.filter((f) => f.section.includes(section))}
              reprocessedState={reprocessedState}
            />
          )
        })}
      </div>
    </>
  )
}

export default SectionSubmissionHistory
