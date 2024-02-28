import React from 'react'
import axios from 'axios'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faCheckCircle,
  faExclamationCircle,
  faXmarkCircle,
  faClock,
} from '@fortawesome/free-solid-svg-icons'
import { getAvailableFileList, download } from '../../actions/reports'
import { getParseErrors } from '../../actions/createXLSReport'

export const formatDate = (dateStr) => new Date(dateStr).toLocaleString()
export const downloadFile = (dispatch, file) => dispatch(download(file))
export const downloadErrorReport = async (file, reportName) => {
  try {
    const promise = axios.get(
      `${process.env.REACT_APP_BACKEND_URL}/data_files/${file.id}/download_error_report/`,
      {
        responseType: 'json',
      }
    )
    const dataPromise = await promise.then((response) => response.data)
    getParseErrors(dataPromise, reportName)
  } catch (error) {
    console.log(error)
  }
}

export const SubmissionSummaryStatusIcon = ({ status }) => {
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
