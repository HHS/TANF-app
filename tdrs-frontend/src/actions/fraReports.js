import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'
import axiosInstance from '../axios-instance'
import { objectToUrlParams } from '../utils/stringUtils'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

export const SET_IS_LOADING_SUBMISSION_HISTORY =
  'SET_IS_LOADING_SUBMISSION_HISTORY'
export const SET_FRA_SUBMISSION_HISTORY = 'SET_FRA_SUBMISSION_HISTORY'
export const SET_IS_UPLOADING_FRA_REPORT = 'SET_IS_UPLOADING_FRA_REPORT'
export const SET_IS_LOADING_FRA_SUBMISSION_STATUS =
  'SET_IS_LOADING_FRA_SUBMISSION_STATUS'
export const SET_FRA_SUBMISSION_STATUS = 'SET_FRA_SUBMISSION_STATUS'

export const getFraSubmissionHistory =
  (
    { stt, reportType, fiscalQuarter, fiscalYear },
    onSuccess = () => null,
    onError = () => null
  ) =>
  async (dispatch) => {
    dispatch({
      type: SET_IS_LOADING_SUBMISSION_HISTORY,
      payload: { isLoadingSubmissionHistory: true },
    })

    try {
      const requestParams = {
        stt: stt.id,
        file_type: reportType,
        year: fiscalYear,
        quarter: fiscalQuarter,
      }

      const response = await axios.get(
        `${BACKEND_URL}/data_files/?${objectToUrlParams(requestParams)}`,
        {
          responseType: 'json',
        }
      )

      dispatch({
        type: SET_FRA_SUBMISSION_HISTORY,
        payload: { submissionHistory: response?.data },
      })

      onSuccess()
    } catch (error) {
      onError(error)
    } finally {
      dispatch({
        type: SET_IS_LOADING_SUBMISSION_HISTORY,
        payload: { isLoadingSubmissionHistory: false },
      })
    }
  }

export const uploadFraReport =
  (
    { stt, reportType, fiscalQuarter, fiscalYear, file, user },
    onSuccess = () => null,
    onError = () => null
  ) =>
  async (dispatch) => {
    dispatch({
      type: SET_IS_UPLOADING_FRA_REPORT,
      payload: { isUploadingFraReport: true },
    })

    const formData = new FormData()
    const fraReportData = {
      file: file,
      original_filename: file.name,
      slug: uuidv4(),
      user: user.id,
      section: reportType,
      year: fiscalYear,
      stt: stt.id,
      quarter: fiscalQuarter,
      ssp: false,
    }
    for (const [key, value] of Object.entries(fraReportData)) {
      formData.append(key, value)
    }

    try {
      const response = await axiosInstance.post(
        `${process.env.REACT_APP_BACKEND_URL}/data_files/`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true,
        }
      )

      dispatch(
        getFraSubmissionHistory({
          stt,
          reportType,
          fiscalQuarter,
          fiscalYear,
        })
      )

      onSuccess(response?.data)
    } catch (error) {
      onError(error)
    } finally {
      dispatch({
        type: SET_IS_UPLOADING_FRA_REPORT,
        payload: { isUploadingFraReport: false },
      })
    }
  }

export const downloadOriginalSubmission =
  ({ id, fileName }) =>
  async (dispatch) => {
    try {
      if (!id) throw new Error('No id provided to download action')

      const response = await axios.get(
        `${BACKEND_URL}/data_files/${id}/download/`,
        { responseType: 'blob' }
      )

      const data = response.data
      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')

      link.href = url
      link.setAttribute('download', fileName)

      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (e) {
      console.error('error downloading file', e)
    }
  }

export const pollFraSubmissionStatus =
  (
    datafile_id,
    tryNumber,
    test = (datafile) => null,
    retry = () => null,
    onSuccess = (datafile) => null,
    onError = (error) => null
  ) =>
  async (dispatch) => {
    const MAX_TRIES = 10 // #

    try {
      if (tryNumber > MAX_TRIES) {
        throw new Error(
          'Exceeded max number of tries to update submission status.'
        )
      } else {
        dispatch({
          type: SET_IS_LOADING_FRA_SUBMISSION_STATUS,
          payload: {
            datafile_id,
            tryNumber,
            isPerformingRequest: true,
            isDone: false,
            error: null,
          },
        })
      }

      const response = await axios.get(
        `${BACKEND_URL}/data_files/${datafile_id}/` // # ?fields=status
      )
      dispatch({
        type: SET_IS_LOADING_FRA_SUBMISSION_STATUS,
        payload: {
          datafile_id,
          isPerformingRequest: false,
        },
      })

      if (!test(response?.data)) {
        retry()
      } else {
        dispatch({
          type: SET_IS_LOADING_FRA_SUBMISSION_STATUS,
          payload: {
            datafile_id,
            isPerformingRequest: false,
            isDone: true,
            error: null,
          },
        })
        dispatch({
          type: SET_FRA_SUBMISSION_STATUS,
          payload: {
            datafile_id,
            datafile: response?.data,
          },
        })
        onSuccess(response?.data)
      }
    } catch (e) {
      dispatch({
        type: SET_IS_LOADING_FRA_SUBMISSION_STATUS,
        payload: {
          datafile_id,
          isPerformingRequest: false,
          isDone: true,
          error: e,
        },
      })
      onError(e)
    }
  }
