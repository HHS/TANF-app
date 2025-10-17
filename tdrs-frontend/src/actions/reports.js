import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'

import axiosInstance from '../axios-instance'
import { logErrorToServer } from '../utils/eventLogger'
import removeFileInputErrorState from '../utils/removeFileInputErrorState'
import { quarters } from '../components/Reports/utils'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

export const SET_FILE = 'SET_FILE'
export const CLEAR_FILE = 'CLEAR_FILE'
export const CLEAR_FILE_LIST = 'CLEAR_FILE_LIST'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const FILE_EXT_ERROR = 'FILE_EXT_ERROR'
export const SET_FILE_SUBMITTED = 'SET_FILE_SUBMITTED'
export const CLEAR_ERROR = 'CLEAR_ERROR'

export const START_FILE_DOWNLOAD = 'START_FILE_DOWNLOAD'
export const FILE_DOWNLOAD_ERROR = 'FILE_DOWNLOAD_ERROR'

export const FETCH_FILE_LIST = 'FETCH_FILE_LIST'
export const SET_FILE_LIST = 'SET_FILE_LIST'
export const FETCH_FILE_LIST_ERROR = 'FETCH_FILE_LIST_ERROR'
export const DOWNLOAD_DIALOG_OPEN = 'DOWNLOAD_DIALOG_OPEN'

export const REINITIALIZE_SUBMITTED_FILES = 'REINITIALIZE_SUBMITTED_FILES'

export const reinitializeSubmittedFiles = (fileType) => (dispatch) => {
  dispatch({ type: REINITIALIZE_SUBMITTED_FILES, payload: { fileType } })
}

export const clearFile =
  ({ section }) =>
  (dispatch) => {
    dispatch({ type: CLEAR_FILE, payload: { section } })
  }

export const clearFileList =
  ({ fileType }) =>
  (dispatch) => {
    // Clean up any DOM error states before clearing Redux state
    removeFileInputErrorState()
    dispatch({ type: CLEAR_FILE_LIST, payload: { fileType } })
  }

export const clearError =
  ({ section }) =>
  (dispatch) => {
    dispatch({ type: CLEAR_ERROR, payload: { section } })
  }

export const getAvailableFileList =
  ({ quarter = 'Q1', stt, year, file_type, section }) =>
  async (dispatch) => {
    dispatch({
      type: FETCH_FILE_LIST,
    })
    try {
      let url = `${BACKEND_URL}/data_files/?year=${year}&stt=${stt.id}&file_type=${file_type}`
      if (quarter) {
        url += `&quarter=${quarter}`
      }
      const response = await axios.get(url, {
        responseType: 'json',
      })
      dispatch({
        type: SET_FILE_LIST,
        payload: {
          data: response?.data,
        },
      })
    } catch (error) {
      dispatch({
        type: FETCH_FILE_LIST_ERROR,
        payload: {
          error,
          year,
          quarter,
          file_type,
          section,
        },
      })
    }
  }

export const download =
  ({ id, quarter = 'Q1', section, year, s3_version_id, fileName }) =>
  async (dispatch) => {
    try {
      if (!id) throw new Error('No id was provided to download action.')
      dispatch({ type: START_FILE_DOWNLOAD })
      const response = await axios.get(
        `${BACKEND_URL}/data_files/${id}/download/`,
        {
          responseType: 'blob',
        }
      )
      const data = response.data

      // Create a link and associate it with the blob returned from the file
      // download - this allows us to trigger the file download dialog without
      // having to change the route or reload the page.
      const url = window.URL.createObjectURL(new Blob([data]))
      const link = document.createElement('a')

      link.href = url
      const fileNameParts = fileName.split('.')
      const baseName = fileNameParts.slice(0, -1).join('.')
      link.setAttribute(
        'download',
        `${baseName} (${year}-${quarter}-${section}).txt`
      )

      document.body.appendChild(link)

      // Click the link to actually prompt the file download
      link.click()

      // Cleanup afterwards to prevent unwanted side effects
      document.body.removeChild(link)
      dispatch({ type: DOWNLOAD_DIALOG_OPEN })
    } catch (error) {
      dispatch({
        type: FILE_DOWNLOAD_ERROR,
        payload: { error, year, quarter, section, s3_version_id },
      })
      return false
    }
  }

// Main Redux action to add files to the state
export const upload =
  ({ file, section }) =>
  async (dispatch) => {
    try {
      dispatch({
        type: SET_FILE,
        payload: {
          file: file,
          fileName: file.name,
          fileType: file.type,
          section,
          uuid: uuidv4(),
        },
      })
    } catch (error) {
      logErrorToServer(SET_FILE_ERROR)
      dispatch({ type: SET_FILE_ERROR, payload: { error, section } })
      return false
    }

    return true
  }

// For now because we consider Program Audit to be the section and program type in the backend, that is what is
// returned to the frontend for the submittedFile's section. However, the frontend maps the Program Audit file's
// section to be the quarter labels. Thus, we need this function to map the backend to the frontend.
const map_section = (fileType, submittedFile) => {
  if (fileType === 'program-integrity-audit') {
    return {
      ...submittedFile,
      section: quarters[submittedFile.quarter],
    }
  }
  return submittedFile
}

export const submit =
  ({
    formattedSections,
    logger,
    quarter,
    setLocalAlertState,
    stt,
    uploadedFiles,
    user,
    year,
    ssp,
    fileType,
  }) =>
  async (dispatch) => {
    const submissionRequests = uploadedFiles.map((file) => {
      const formData = new FormData()
      const dataFile = {
        file: file.file,
        original_filename: file.fileName,
        slug: file.uuid,
        user: user.id,
        section: file.section,
        year,
        stt,
        quarter: quarter ? quarter : file.quarter,
        ssp,
        is_program_audit: file.is_program_audit ? file.is_program_audit : false,
      }
      for (const [key, value] of Object.entries(dataFile)) {
        formData.append(key, value)
      }
      return axiosInstance.post(
        `${process.env.REACT_APP_BACKEND_URL}/data_files/`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          withCredentials: true,
        }
      )
    })

    return Promise.all(submissionRequests)
      .then((responses) => {
        setLocalAlertState({
          active: true,
          type: 'success',
          message: `Successfully submitted section(s): ${formattedSections} on ${new Date().toDateString()}`,
        })
        removeFileInputErrorState()

        const submittedFiles = responses.reduce((result, response) => {
          const submittedFile = map_section(fileType, response?.data)
          dispatch({
            type: SET_FILE_SUBMITTED,
            payload: { submittedFile },
          })
          result.push(
            `${submittedFile?.original_filename} (${submittedFile?.extension})`
          )
          return result
        }, [])

        // Create LogEntries in Django for each created ReportFile
        logger.alert(
          `Submitted ${
            submittedFiles.length
          } data file(s): ${submittedFiles.join(', ')}`,
          {
            files: responses.map((response) => response?.data?.id),
            activity: 'upload',
          }
        )
      })
      .catch((error) => {
        const error_response = error.response?.data
        const msg = error_response?.non_field_errors
          ? error_response.non_field_errors[0]
          : error_response?.detail
            ? error_response.detail
            : error_response?.file
              ? error_response.file
              : null
        setLocalAlertState({
          active: true,
          type: 'error',
          message: ''.concat(error.message, ': ', msg),
        })
      })
  }

export const SET_SELECTED_STT = 'SET_SELECTED_STT'

export const setStt = (stt) => (dispatch) => {
  dispatch({ type: SET_SELECTED_STT, payload: { stt } })
}
