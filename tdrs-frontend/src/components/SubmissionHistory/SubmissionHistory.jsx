import React from 'react'
import axios from 'axios'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fileUploadSections } from '../../reducers/reports'
import Paginator from '../Paginator'
import { getAvailableFileList, download } from '../../actions/reports'
import { useEffect } from 'react'
import { useState } from 'react'
import { getParseErrors } from '../../actions/createXLSReport'

const formatDate = (dateStr) => new Date(dateStr).toLocaleString()

const SubmissionHistoryRow = ({ file }) => {
  const dispatch = useDispatch()

  const downloadFile = () => dispatch(download(file))
  const errorFileName = `${file.year}-${file.quarter}-${file.section}`

  const returned_errors = async () => {
    try {
      const promise = axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/parsing/parsing_errors/?file=${file.id}`,
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

  return (
    <tr>
      <td>{formatDate(file.createdAt)}</td>
      <td>{file.submittedBy}</td>
      <td>
        <button className="section-download" onClick={downloadFile}>
          {file.fileName}
        </button>
      </td>
      <td>
        {file.hasError > 0 ? (
          <button className="section-download" onClick={returned_errors}>
            {file.year}-{file.quarter}-{file.section}
          </button>
        ) : (
          'Currently Unavailable'
        )}
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

  const pages =
    files && files.length > pageSize ? Math.ceil(files.length / pageSize) : 1
  const pageStart = (resultsPage - 1) * pageSize
  const pageEnd = Math.min(files.length, pageStart + pageSize)

  return (
    <div className="submission-history-section">
      <table className="usa-table usa-table--striped">
        <caption>{`Section ${section} - ${label}`}</caption>
        {files && files.length > 0 ? (
          <>
            <thead>
              <tr>
                <th>Submitted On</th>
                <th>Submitted By</th>
                <th>File Name</th>
                <th>Error Reports (In development)</th>
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
