import {
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  FILE_EXT_ERROR,
  CLEAR_ERROR,
  SET_SELECTED_STT,
  SET_FILE_LIST,
  CLEAR_FILE_LIST,
  SET_FILE_SUBMITTED,
  REINITIALIZE_SUBMITTED_FILES,
  FETCH_FILE_LIST,
  FETCH_FILE_LIST_ERROR,
  SET_TANF_SUBMISSION_STATUS,
} from '../actions/reports'

import { programIntegrityAuditLabels } from '../components/Reports/utils'

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
  program_type: dataFile.program_type,
  uuid: dataFile.slug,
  year: dataFile.year,
  s3_version_id: dataFile.s3_version_id,
  createdAt: dataFile.created_at,
  submittedBy: dataFile.submitted_by,
  hasError: dataFile.has_error,
  summary: dataFile.summary,
  latest_reparse_file_meta: dataFile.latest_reparse_file_meta,
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
  year: '',
  stt: '',
  quarter: '',
  fileType: '',
  loading: false,
}

const reports = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case FETCH_FILE_LIST: {
      return {
        ...state,
        loading: true,
      }
    }
    case REINITIALIZE_SUBMITTED_FILES: {
      const { fileType } = payload
      const sections =
        fileType === 'program-integrity-audit'
          ? programIntegrityAuditLabels
          : fileUploadSections

      return {
        ...state,
        submittedFiles: sections.map((section) => ({
          section,
          fileName: null,
          error: null,
          uuid: null,
          fileType: null,
        })),
      }
    }
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
        loading: false,
      }
    }
    case FETCH_FILE_LIST_ERROR: {
      return {
        ...state,
        loading: false,
      }
    }
    case SET_FILE_SUBMITTED: {
      const { submittedFile } = payload
      return {
        ...state,
        submittedFiles: state.submittedFiles.map((file) =>
          // Match by uuid (slug) or section to handle transformed files because submitting PIA files changes
          // their section from `Quarter X (Month Y to Month Z)` to `Program Audit` for the backend.
          submittedFile?.slug === file.uuid ||
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
      const { fileType } = payload
      return {
        ...state,
        files: initialState.files,
        submittedFiles:
          fileType !== 'program-integrity-audit'
            ? initialState.submittedFiles
            : programIntegrityAuditLabels.map((section) => ({
                section,
                fileName: null,
                error: null,
                uuid: null,
                fileType: null,
              })),
      }
    }
    case SET_FILE_ERROR: {
      const { error, section } = payload
      const updatedFiles = getUpdatedFiles({ state, section, error })
      return { ...state, submittedFiles: updatedFiles }
    }
    case FILE_EXT_ERROR: {
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
        id: file.id,
        fileType: file.fileType,
      })
      return { ...state, submittedFiles: updatedFiles }
    }
    case SET_SELECTED_STT: {
      const { stt } = payload
      return { ...state, stt }
    }
    case SET_TANF_SUBMISSION_STATUS: {
      const { datafile_id, datafile } = payload
      const files = state.files.map((f) =>
        f.id === datafile_id ? serializeApiDataFile(datafile) : f
      )

      return { ...state, files }
    }
    default:
      return state
  }
}

export default reports
