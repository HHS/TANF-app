import React from 'react'
import { useDispatch } from 'react-redux'
import {
  SubmissionSummaryStatusIcon,
  formatDate,
  hasReparsed,
  getReprocessedDate,
  downloadFile,
  getErrorReportStatus,
} from './helpers'
import { ReprocessedButton } from './ReprocessedModal'

const MonthSubRow = ({ data }) =>
  data ? (
    <>
      <th scope="row">{data.month}</th>
      <td>{data.total_errors}</td>
    </>
  ) : (
    <>
      <th scope="row">-</th>
      <td>N/A</td>
    </>
  )

const TotalAggregatesRow = ({ file, reprocessedState }) => {
  const dispatch = useDispatch()
  const reprocessedDate = formatDate(getReprocessedDate(file))
  return (
    <>
      <tr>
        <th scope="rowgroup" rowSpan={3}>
          {formatDate(file.createdAt) + ' by ' + file.submittedBy}
          {hasReparsed(file) && (
            <ReprocessedButton
              date={reprocessedDate}
              reprocessedState={reprocessedState}
            />
          )}
        </th>

        <th scope="rowgroup" rowSpan={3}>
          <button
            className="section-download"
            onClick={() => downloadFile(dispatch, file)}
          >
            {file.fileName}
          </button>
        </th>

        <MonthSubRow data={file?.summary?.case_aggregates?.months?.[0]} />

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
          {getErrorReportStatus(file)}
        </th>
      </tr>
      <tr>
        <MonthSubRow data={file?.summary?.case_aggregates?.months?.[1]} />
      </tr>
      <tr>
        <MonthSubRow data={file?.summary?.case_aggregates?.months?.[2]} />
      </tr>
    </>
  )
}

export const TotalAggregatesTable = ({ files, reprocessedState }) => (
  <>
    <thead>
      <tr>
        <th scope="col" rowSpan={2}>
          Submitted On
        </th>
        <th scope="col" rowSpan={2}>
          File Name
        </th>
        <th scope="col" rowSpan={2}>
          Month
        </th>
        <th scope="col" rowSpan={2}>
          Total Errors
        </th>
        <th scope="col" rowSpan={2}>
          Status
        </th>
        <th scope="col" rowSpan={2}>
          Error Reports
        </th>
      </tr>
    </thead>
    <tbody>
      {files.map((file) => (
        <TotalAggregatesRow
          key={file.id}
          file={file}
          reprocessedState={reprocessedState}
        />
      ))}
    </tbody>
  </>
)
