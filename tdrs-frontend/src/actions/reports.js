import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'

import axiosInstance from '../axios-instance'
import { logErrorToServer } from '../utils/eventLogger'
import removeFileInputErrorState from '../utils/removeFileInputErrorState'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

export const SET_FILE = 'SET_FILE'
export const CLEAR_FILE = 'CLEAR_FILE'
export const CLEAR_FILE_LIST = 'CLEAR_FILE_LIST'
export const SET_FILE_ERROR = 'SET_FILE_ERROR'
export const SET_FILE_SUBMITTED = 'SET_FILE_SUBMITTED'
export const CLEAR_ERROR = 'CLEAR_ERROR'

export const START_FILE_DOWNLOAD = 'START_FILE_DOWNLOAD'
export const FILE_DOWNLOAD_ERROR = 'FILE_DOWNLOAD_ERROR'

export const FETCH_FILE_LIST = 'FETCH_FILE_LIST'
export const SET_FILE_LIST = 'SET_FILE_LIST'
export const FETCH_FILE_LIST_ERROR = 'FETCH_FILE_LIST_ERROR'
export const DOWNLOAD_DIALOG_OPEN = 'DOWNLOAD_DIALOG_OPEN'

export const clearFile =
  ({ section }) =>
  (dispatch) => {
    dispatch({ type: CLEAR_FILE, payload: { section } })
  }

export const clearFileList = () => (dispatch) => {
  dispatch({ type: CLEAR_FILE_LIST })
}

export const clearError =
  ({ section }) =>
  (dispatch) => {
    dispatch({ type: CLEAR_ERROR, payload: { section } })
  }

/**
   Get a list of files that can be downloaded, mainly used to decide
   if the download button should be present.
*/
export const getAvailableFileList =
  ({ quarter = 'Q1', stt, year }) =>
  async (dispatch) => {
    dispatch({
      type: FETCH_FILE_LIST,
    })
    try {
      const response = await axios.get(
        `${BACKEND_URL}/data_files/?year=${year}&quarter=${quarter}&stt=${stt.id}`,
        {
          responseType: 'json',
        }
      )
      dispatch({
        type: SET_FILE_LIST,
        payload: {
          data: response?.data?.results,
        },
      })
    } catch (error) {
      dispatch({
        type: FETCH_FILE_LIST_ERROR,
        payload: {
          error,
          year,
          quarter,
        },
      })
    }
  }

export const download =
  ({ id, quarter = 'Q1', section, year }) =>
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
      link.setAttribute('download', `${year}.${quarter}.${section}.txt`)

      document.body.appendChild(link)

      // Click the link to actually prompt the file download
      link.click()

      // Cleanup afterwards to prevent unwanted side effects
      document.body.removeChild(link)
      dispatch({ type: DOWNLOAD_DIALOG_OPEN })
    } catch (error) {
      dispatch({
        type: FILE_DOWNLOAD_ERROR,
        payload: { error, year, quarter, section },
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
        quarter,
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

    Promise.all(submissionRequests)
      .then((responses) => {
        setLocalAlertState({
          active: true,
          type: 'success',
          message: `Successfully submitted section(s): ${formattedSections} on ${new Date().toDateString()}`,
        })
        removeFileInputErrorState()

        const submittedFiles = responses.reduce((result, response) => {
          dispatch({
            type: SET_FILE_SUBMITTED,
            payload: { data: response?.data },
          })
          return `${response?.data?.original_filename} (${response?.data?.extension})`
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
      .catch((error) => console.error(error))
  }

export const SET_SELECTED_STT = 'SET_SELECTED_STT'
export const SET_SELECTED_YEAR = 'SET_SELECTED_YEAR'
export const SET_SELECTED_QUARTER = 'SET_SELECTED_QUARTER'

export const setStt = (stt) => (dispatch) => {
  dispatch({ type: SET_SELECTED_STT, payload: { stt } })
}
export const setYear = (year) => (dispatch) => {
  dispatch({ type: SET_SELECTED_YEAR, payload: { year } })
}

export const setQuarter = (quarter) => (dispatch) => {
  dispatch({ type: SET_SELECTED_QUARTER, payload: { quarter } })
}
