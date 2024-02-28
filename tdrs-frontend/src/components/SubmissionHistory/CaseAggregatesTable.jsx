import React from 'react'
import { useDispatch } from 'react-redux'
import {
  SubmissionSummaryStatusIcon,
  formatDate,
  downloadFile,
  downloadErrorReport,
} from './helpers'

const MonthSubRow = ({ data }) =>
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

const CaseAggregatesRow = ({ file }) => {
  const dispatch = useDispatch()
  const errorFileName = `${file.year}-${file.quarter}-${file.section}`

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
          <button
            className="section-download"
            onClick={() => downloadFile(dispatch, file)}
          >
            {file.fileName}
          </button>
        </th>

        <MonthSubRow data={file?.summary?.case_aggregates?.months?.[0]} />

        <th scope="rowgroup" rowSpan={3}>
          {file.summary?.case_aggregates?.rejected || 'N/A'}
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
              <button
                className="section-download"
                onClick={() => downloadErrorReport(file, errorFileName)}
              >
                {errorFileName}.xlsx
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
        <MonthSubRow data={file?.summary?.case_aggregates?.months?.[1]} />
      </tr>
      <tr>
        <MonthSubRow data={file?.summary?.case_aggregates?.months?.[2]} />
      </tr>
    </>
  )
}

export const CaseAggregatesTable = ({ files }) => (
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
        <th scope="col" rowSpan={2}>
          Status
        </th>
        <th scope="col" rowSpan={2}>
          Error Reports (In development)
        </th>
      </tr>
    </thead>
    <tbody>
      {files.map((file) => (
        <CaseAggregatesRow key={file.id} file={file} />
      ))}
    </tbody>
  </>
)
