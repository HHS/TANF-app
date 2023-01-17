import React from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fileUploadSections } from '../../reducers/reports'
import Paginator from '../Paginator'
import {
  clearFileList,
  setYear,
  setStt,
  setQuarter,
  getAvailableFileList,
  setFileType,
} from '../../actions/reports'

const SubmissionHistoryRow = () => (
  <tr>
    <td>12/12/12 12:12pm</td>
    <td>Horace Slughorn</td>
    <td>File.jpg</td>
  </tr>
)

SubmissionHistoryRow.propTypes = {}

const SectionSubmissionHistory = ({ section, label, filterValues }) => {
  const dispatch = useDispatch()

  // Retrieve the files matching the selected year, quarter, and ssp.

  const getFiles = (page) => {
    console.log('hello?')
    dispatch(
      getAvailableFileList({
        ...filterValues,
        section: label,
        page,
      })
    )
  }

  return (
    <div>
      <label className="usa-label text-bold">{`Section ${section} - ${label}`}</label>

      <table className="usa-table usa-table--striped">
        <thead>
          <tr>
            <th>Submitted On</th>
            <th>Submitted By</th>
            <th>File Name</th>
          </tr>
        </thead>
        <tbody>
          <SubmissionHistoryRow />
          <SubmissionHistoryRow />
          <SubmissionHistoryRow />
          <SubmissionHistoryRow />
          <SubmissionHistoryRow />
        </tbody>
      </table>

      <Paginator onChange={(page) => getFiles(page)} selected={1} pages={5} />
    </div>
  )
}

SectionSubmissionHistory.propTypes = {
  section: PropTypes.number,
  label: PropTypes.string,
  filterValues: PropTypes.shape({
    stt: PropTypes.number,
    file_type: PropTypes.string,
    quarter: PropTypes.string,
    year: PropTypes.string,
  }),
}

const SubmissionHistory = ({ filterValues }) => (
  <div>
    {fileUploadSections.map((section, index) => (
      <SectionSubmissionHistory
        key={section}
        section={index + 1}
        label={section}
        filterValues={filterValues}
      />
    ))}
  </div>
)

SubmissionHistory.propTypes = {
  filterValues: PropTypes.shape({
    stt: PropTypes.number,
    file_type: PropTypes.string,
    quarter: PropTypes.string,
    year: PropTypes.string,
  }),
}

export default SubmissionHistory
