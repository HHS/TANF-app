import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'
import axiosInstance from '../axios-instance'
import { objectToUrlParams } from '../utils/stringUtils'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

export const SET_IS_LOADING_SUBMISSION_HISTORY =
  'SET_IS_LOADING_SUBMISSION_HISTORY'
export const SET_FRA_SUBMISSION_HISTORY = 'SET_FRA_SUBMISSION_HISTORY'
export const SET_IS_UPLOADING_FRA_REPORT = 'SET_IS_UPLOADING_FRA_REPORT'

export const getFraSubmissionHistory =
  ({ stt, reportType, fiscalQuarter, fiscalYear }, onSuccess, onError) =>
  async (dispatch) => {
    dispatch({
      type: SET_IS_LOADING_SUBMISSION_HISTORY,
      payload: { isLoadingSubmissionHistory: true },
    })

    // do work
    try {
      console.log('params', { stt, reportType, fiscalQuarter, fiscalYear })

      const requestParams = {
        stt: stt.id,
        file_type: reportType,
        year: fiscalYear,
        quarter: fiscalQuarter,
      }
      console.log('params', requestParams)
      console.log(objectToUrlParams(requestParams))

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
    }

    dispatch({
      type: SET_IS_LOADING_SUBMISSION_HISTORY,
      payload: { isLoadingSubmissionHistory: false },
    })
  }

export const uploadFraReport =
  (
    { stt, reportType, fiscalQuarter, fiscalYear, file, user },
    onSuccess,
    onError
  ) =>
  async (dispatch) => {
    dispatch({
      type: SET_IS_UPLOADING_FRA_REPORT,
      payload: { isUploadingFraReport: true },
    })

    // do work
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
      onSuccess()
    } catch (error) {
      onError(error)
    }

    dispatch({
      type: SET_IS_UPLOADING_FRA_REPORT,
      payload: { isUploadingFraReport: false },
    })
  }
