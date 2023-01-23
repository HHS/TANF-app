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
  download,
} from '../../actions/reports'
import { useEffect } from 'react'
import { useState } from 'react'
import Button from '../Button'

const SubmissionHistoryRow = ({ file }) => {
  const dispatch = useDispatch()

  const downloadFile = () => dispatch(download(file))

  return (
    <tr>
      <td>{file.createdAt}</td>
      <td>{file.submittedBy}</td>
      <td>
        <button onClick={downloadFile}>{file.fileName}</button>
      </td>
    </tr>
  )
}

SubmissionHistoryRow.propTypes = {
  file: PropTypes.object,
}

const SectionSubmissionHistory = ({ section, label, files }) => {
  const pageSize = 5
  const [resultsPage, setResultsPage] = useState(1)

  const pageStart = (resultsPage - 1) * pageSize
  const pageEnd = Math.min(files.length, pageStart + pageSize)

  return (
    <div>
      <label className="usa-label text-bold">{`Section ${section} - ${label}`}</label>
      {files && files.length > 0 ? (
        <table className="usa-table usa-table--striped">
          <thead>
            <tr>
              <th>Submitted On</th>
              <th>Submitted By</th>
              <th>File Name</th>
            </tr>
          </thead>
          <tbody>
            {files.slice(pageStart, pageEnd).map((file) => (
              <SubmissionHistoryRow key={file.id} file={file} />
            ))}
          </tbody>
        </table>
      ) : (
        <p>No data available.</p>
      )}

      <Paginator
        onChange={(page) => setResultsPage(page)}
        selected={resultsPage}
        pages={
          files && files.length > pageSize
            ? Math.ceil(files.length / pageSize)
            : 1
        }
      />
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
          files={files.filter((f) => f.section === section)}
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
