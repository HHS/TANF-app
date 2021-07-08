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
} from '../actions/reports'

const getFileIndex = (files, section) =>
  files.findIndex((currentFile) => currentFile.section === section)
const getFile = (files, section) =>
  files.find((currentFile) => currentFile.section === section)

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
  const oldFileIndex = getFileIndex(state.files, section)
  const updatedFiles = [...state.files]
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

const initialState = {
  files: fileUploadSections.map((section) => ({
    section,
    fileName: null,
    error: null,
    uuid: null,
    fileType: null,
  })),
  year: '',
  stt: '',
  quarter: '',
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
      return { ...state, files: updatedFiles }
    }
    case SET_FILE_LIST: {
      const { data } = payload
      return {
        ...state,
        files: state.files.map((file) => {
          const dataFile = getFile(data, file.section)
          return dataFile
            ? {
                id: dataFile.id,
                fileName: dataFile.original_filename,
                fileType: dataFile.extension,
                quarter: dataFile.quarter,
                section: dataFile.section,
                uuid: dataFile.slug,
                year: dataFile.year,
              }
            : file
        }),
      }
    }
    case CLEAR_FILE: {
      const { section } = payload
      const updatedFiles = getUpdatedFiles({ state, section })
      return { ...state, files: updatedFiles }
    }
    case CLEAR_FILE_LIST: {
      return { ...state, files: initialState.files }
    }
    case SET_FILE_ERROR: {
      const { error, section } = payload
      const updatedFiles = getUpdatedFiles({ state, section, error })
      return { ...state, files: updatedFiles }
    }
    case CLEAR_ERROR: {
      const { section } = payload
      const file = getFile(state.files, section)
      const updatedFiles = getUpdatedFiles({
        state,
        fileName: file.fileName,
        section,
        uuid: file.uuid,
        fileType: file.fileType,
      })
      return { ...state, files: updatedFiles }
    }
    case SET_SELECTED_YEAR: {
      const { year } = payload
      return { ...state, year: parseInt(year) }
    }
    case SET_SELECTED_STT: {
      const { stt } = payload
      return { ...state, stt }
    }
    case SET_SELECTED_QUARTER: {
      const { quarter } = payload
      return { ...state, quarter }
    }
    default:
      return state
  }
}

export default reports
