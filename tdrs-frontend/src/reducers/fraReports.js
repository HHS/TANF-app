import {
  SET_IS_LOADING_SUBMISSION_HISTORY,
  SET_FRA_SUBMISSION_HISTORY,
  SET_IS_UPLOADING_FRA_REPORT,
  SET_FRA_SUBMISSION_STATUS,
} from '../actions/fraReports'
import { serializeApiDataFile } from './reports'

const initialState = {
  isLoadingSubmissionHistory: false,
  isUploadingFraReport: false,
  submissionHistory: null,
}

const fraReports = (state = initialState, action) => {
  const { type, payload = {} } = action

  switch (type) {
    case SET_IS_LOADING_SUBMISSION_HISTORY: {
      const { isLoadingSubmissionHistory } = payload
      return {
        ...state,
        isLoadingSubmissionHistory,
      }
    }
    case SET_FRA_SUBMISSION_HISTORY: {
      const { submissionHistory } = payload
      return {
        ...state,
        submissionHistory: submissionHistory
          ? submissionHistory.map((f) => serializeApiDataFile(f))
          : null,
      }
    }
    case SET_IS_UPLOADING_FRA_REPORT: {
      const { isUploadingFraReport } = payload
      return {
        ...state,
        isUploadingFraReport,
      }
    }
    case SET_FRA_SUBMISSION_STATUS: {
      const { datafile_id, datafile } = payload
      const submissionHistory = state.submissionHistory.map((f) =>
        f.id === datafile_id ? serializeApiDataFile(datafile) : f
      )

      return { ...state, submissionHistory }
    }
    default:
      return state
  }
}

export default fraReports
