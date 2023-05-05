import {
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  CLEAR_ERROR,
  SET_SELECTED_YEAR,
  SET_SELECTED_STT,
  SET_SELECTED_QUARTER,
  SET_FILE_LIST,
  CLEAR_FILE_LIST,
  SET_FILE_SUBMITTED,
  SET_FILE_TYPE,
  SET_CURRENT_SUBMISSION,
  SET_LOADING_CURRENT_SUBMISSION,
  SET_CURRENT_SUBMISSION_ERROR,
} from '../actions/reports'

const getFileIndex = (files, section) =>
  files.findIndex((currentFile) => currentFile.section.includes(section))
const getFile = (files, section) =>
  files
    .sort((a, b) => b.id - a.id)
    .find((currentFile) => currentFile.section.includes(section))

export const fileUploadSections = [
  'Active Case Data',
  'Closed Case Data',
  'Aggregate Data',
  'Stratum Data',
]

export const getUpdatedFiles = ({
  state,
  fileName,
  section,
  id = null,
  uuid = null,
  fileType = null,
  error = null,
  file = null,
}) => {
  const oldFileIndex = getFileIndex(state?.submittedFiles, section)
  const updatedFiles = [...state.submittedFiles]
  updatedFiles[oldFileIndex] = {
    id,
    file,
    section,
    fileName,
    error,
    uuid,
    fileType,
  }

  return updatedFiles
}

export const serializeApiDataFile = (dataFile) => ({
  id: dataFile.id,
  fileName: dataFile.original_filename,
  fileType: dataFile.extension,
  quarter: dataFile.quarter,
  section: dataFile.section,
  uuid: dataFile.slug,
  year: dataFile.year,
  s3_version_id: dataFile.s3_version_id,
  createdAt: dataFile.created_at,
  submittedBy: dataFile.submitted_by,
  hasError: dataFile.has_error,
})

const initialState = {
  files: [],
  submittedFiles: fileUploadSections.map((section) => ({
    section,
    fileName: null,
    error: null,
    uuid: null,
    fileType: null,
  })),
  isLoadingCurrentSubmission: false,
  currentSubmissionError: null,
  year: '',
  stt: '',
  quarter: '',
  fileType: 'tanf',
}

const reports = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_FILE: {
      const { file, fileName, section, uuid, fileType } = payload
      const updatedFiles = getUpdatedFiles({
        state,
        fileName,
        section,
        uuid,
        fileType,
        file,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case SET_FILE_LIST: {
      const { data } = payload
      return {
        ...state,
        files: data.map((f) => serializeApiDataFile(f)),
      }
    }
    case SET_CURRENT_SUBMISSION: {
      const { data } = payload
      return {
        ...state,
        isLoadingCurrentSubmission: false,
        currentSubmissionError: null,
        submittedFiles: fileUploadSections.map((section) => {
          const file = getFile(data, section)
          if (file) {
            return serializeApiDataFile(file)
          }

          return serializeApiDataFile({
            id: null,
            original_filename: null,
            extension: null,
            quarter: null,
            section: section,
            slug: null,
            year: null,
            s3_version_id: null,
            created_at: null,
            submitted_by: null,
            has_error: null,
          })
        }),
      }
    }
    case SET_LOADING_CURRENT_SUBMISSION: {
      const { isLoadingCurrentSubmission } = payload
      return { ...state, isLoadingCurrentSubmission }
    }
    case SET_CURRENT_SUBMISSION_ERROR: {
      const { error } = payload
      return {
        ...state,
        isLoadingCurrentSubmission: false,
        currentSubmissionError: error,
      }
    }
    case SET_FILE_SUBMITTED: {
      const { submittedFile } = payload
      return {
        ...state,
        submittedFiles: state.submittedFiles.map((file) =>
          submittedFile?.section.includes(file.section)
            ? serializeApiDataFile(submittedFile)
            : file
        ),
      }
    }
    case CLEAR_FILE: {
      const { section } = payload
      const updatedFiles = getUpdatedFiles({ state, section })
      return { ...state, submittedFiles: updatedFiles }
    }
    case CLEAR_FILE_LIST: {
      return {
        ...state,
        files: initialState.files,
        submittedFiles: initialState.submittedFiles,
      }
    }
    case SET_FILE_ERROR: {
      const { error, section } = payload
      const updatedFiles = getUpdatedFiles({ state, section, error })
      return { ...state, submittedFiles: updatedFiles }
    }
    case CLEAR_ERROR: {
      const { section } = payload
      const file = getFile(state.submittedFiles, section)
      const updatedFiles = getUpdatedFiles({
        state,
        fileName: file.fileName,
        section,
        uuid: file.uuid,
        fileType: file.fileType,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case SET_SELECTED_YEAR: {
      const { year } = payload
      return { ...state, year }
    }
    case SET_SELECTED_STT: {
      const { stt } = payload
      return { ...state, stt }
    }
    case SET_SELECTED_QUARTER: {
      const { quarter } = payload
      return { ...state, quarter }
    }
    case SET_FILE_TYPE: {
      const { fileType } = payload
      return { ...state, fileType }
    }
    default:
      return state
  }
}

export default reports
