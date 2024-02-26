import React from 'react'
import axios from 'axios'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fileUploadSections } from '../../reducers/reports'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faCheckCircle,
  faExclamationCircle,
  faXmarkCircle,
  faClock,
} from '@fortawesome/free-solid-svg-icons'
import Paginator from '../Paginator'
import { getAvailableFileList, download } from '../../actions/reports'
import { useEffect } from 'react'
import { useState } from 'react'
import { getParseErrors } from '../../actions/createXLSReport'

const formatDate = (dateStr) => new Date(dateStr).toLocaleString()

const SubmissionSummaryStatusIcon = ({ status }) => {
  let icon = null
  let color = null

  switch (status) {
    case 'Pending':
      icon = faClock
      color = '#005EA2'
      break
    case 'Accepted':
      icon = faCheckCircle
      color = '#40bb45'
      break
    case 'Partially Accepted with Errors':
      icon = faExclamationCircle
      color = '#ec4e11'
      break
    case 'Accepted with Errors':
      icon = faExclamationCircle
      color = '#ec4e11'
      break
    case 'Rejected':
      icon = faXmarkCircle
      color = '#bb0000'
      break
    default:
      break
  }
  return (
    <FontAwesomeIcon className="margin-right-1" icon={icon} color={color} />
  )
}

const CaseAggregatesHeader = ({ section }) =>
  section === 1 || section === 2 ? (
    <>
      <th scope="col" rowSpan={2}>
        Month
      </th>
      <th scope="col" rowSpan={2}>
        Cases Without Errors
      </th>
      <th scope="col" rowSpan={2}>
        Cases With Errors
      </th>
      <th scope="col" rowSpan={2}>
        Records Unable To Process
      </th>
    </>
  ) : (
    <>
      <th scope="col" rowSpan={2}>
        Month
      </th>
      <th scope="col" rowSpan={2}>
        Total
      </th>
      <th scope="col" rowSpan={2}>
        Cases With Errors
      </th>
    </>
  )

const CaseAggregatesRow = ({ data, section }) =>
  section === 1 || section === 2 ? (
    data ? (
      <>
        <th scope="row">{data.month}</th>
        <td>{data.accepted_without_errors}</td>
        <td>{data.accepted_with_errors}</td>
      </>
    ) : (
      <>
        <th scope="row">-</th>
        <td>N/A</td>
        <td>N/A</td>
      </>
    )
  ) : data ? (
    <>
      <th scope="row">{data.month}</th>
      <td>{data.total}</td>
    </>
  ) : (
    <>
      <th scope="row">-</th>
      <td>N/A</td>
    </>
  )

const SubmissionHistoryRow = ({ file }) => {
  const dispatch = useDispatch()

  const downloadFile = () => dispatch(download(file))
  const errorFileName = `${file.year}-${file.quarter}-${file.section}`

  const returned_errors = async () => {
    try {
      const promise = axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/data_files/${file.id}/download_error_report/`,
        {
          responseType: 'json',
        }
      )
      const dataPromise = await promise.then((response) => response.data)
      getParseErrors(dataPromise, errorFileName)
    } catch (error) {
      console.log(error)
    }
  }

  const section_index = (element) => file.section.includes(element)

  const section = fileUploadSections.findIndex(section_index) + 1

  return (
    <>
      <tr>
        <th scope="rowgroup" rowSpan={3}>
          {formatDate(file.createdAt)}
        </th>
        <th scope="rowgroup" rowSpan={3}>
          {file.submittedBy}
        </th>
        <th scope="rowgroup" rowSpan={3}>
          <button className="section-download" onClick={downloadFile}>
            {file.fileName}
          </button>
        </th>
        <CaseAggregatesRow
          data={
            file.summary &&
            file.summary.case_aggregates &&
            file.summary.case_aggregates.months
              ? file.summary.case_aggregates.months[0]
              : null
          }
          section={section}
        />

        <th scope="rowgroup" rowSpan={3}>
          {file.summary &&
          file.summary.case_aggregates &&
          file.summary.case_aggregates.months
            ? file.summary.case_aggregates.rejected
            : 'N/A'}
        </th>

        <th scope="rowgroup" rowSpan={3}>
          <span>
            <SubmissionSummaryStatusIcon
              status={file.summary ? file.summary.status : 'Pending'}
            />
          </span>
          {file.summary && file.summary.status
            ? file.summary.status
            : 'Pending'}
        </th>

        <th scope="rowgroup" rowSpan={3}>
          {file.summary &&
          file.summary.status &&
          file.summary.status !== 'Pending' ? (
            file.hasError > 0 ? (
              <button className="section-download" onClick={returned_errors}>
                {file.year}-{file.quarter}-{file.section}.xlsx
              </button>
            ) : (
              'No Errors'
            )
          ) : (
            'Pending'
          )}
        </th>
      </tr>

      <tr>
        <CaseAggregatesRow
          data={
            file.summary &&
            file.summary.case_aggregates &&
            file.summary.case_aggregates.months
              ? file.summary.case_aggregates.months[1]
              : null
          }
          section={section}
        />
      </tr>
      <tr>
        <CaseAggregatesRow
          data={
            file.summary &&
            file.summary.case_aggregates &&
            file.summary.case_aggregates.months
              ? file.summary.case_aggregates.months[2]
              : null
          }
          section={section}
        />
      </tr>
    </>
  )
}

SubmissionHistoryRow.propTypes = {
  file: PropTypes.object,
}

const SectionSubmissionHistory = ({ section, label, files }) => {
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
        <caption>{`Section ${section} - ${label}`}</caption>
        {files && files.length > 0 ? (
          <>
            <thead>
              <tr>
                <th scope="col" rowSpan={2}>
                  Submitted On
                </th>
                <th scope="col" rowSpan={2}>
                  Submitted By
                </th>
                <th scope="col" rowSpan={2}>
                  File Name
                </th>
                <CaseAggregatesHeader section={section} />
                <th scope="col" rowSpan={2}>
                  Status
                </th>
                <th scope="col" rowSpan={2}>
                  Error Reports (In development)
                </th>
              </tr>
            </thead>
            <tbody>
              {files.slice(pageStart, pageEnd).map((file) => (
                <SubmissionHistoryRow key={file.id} file={file} />
              ))}
            </tbody>
          </>
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

SectionSubmissionHistory.propTypes = {
  section: PropTypes.number,
  label: PropTypes.string,
  filterValues: PropTypes.shape({
    stt: PropTypes.object,
    file_type: PropTypes.string,
    quarter: PropTypes.string,
    year: PropTypes.string,
  }),
  files: PropTypes.array,
}

const SubmissionHistory = ({ filterValues }) => {
  const dispatch = useDispatch()
  const [hasFetchedFiles, setHasFetchedFiles] = useState(false)
  const { files } = useSelector((state) => state.reports)

  useEffect(() => {
    if (!hasFetchedFiles) {
      dispatch(getAvailableFileList(filterValues))
      setHasFetchedFiles(true)
    }
  }, [hasFetchedFiles, files, dispatch, filterValues])

  return (
    <div>
      {fileUploadSections.map((section, index) => (
        <SectionSubmissionHistory
          key={section}
          section={index + 1}
          label={section}
          filterValues={filterValues}
          files={files.filter((f) => f.section.includes(section))}
        />
      ))}
    </div>
  )
}

SubmissionHistory.propTypes = {
  filterValues: PropTypes.shape({
    stt: PropTypes.object,
    file_type: PropTypes.string,
    quarter: PropTypes.string,
    year: PropTypes.string,
  }),
}

export default SubmissionHistory
