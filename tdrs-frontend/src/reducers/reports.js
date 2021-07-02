import {
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  CLEAR_ERROR,
  SET_SELECTED_YEAR,
  SET_SELECTED_STT,
  SET_SELECTED_QUARTER,
  SET_FILE_LIST,
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

export const getUpdatedFiles = (
  file,
  state,
  fileName,
  section,
  uuid = null,
  fileType = null,
  error = null,
  data = ''
) => {
  const oldFileIndex = getFileIndex(state.files, section)
  const updatedFiles = [...state.files]
  updatedFiles[oldFileIndex] = {
    file,
    section,
    fileName,
    data,
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
      const updatedFiles = getUpdatedFiles(
        file,
        state,
        fileName,
        section,
        uuid,
        fileType
      )
      return { ...state, files: updatedFiles }
    }
    case SET_FILE_LIST: {
      const { data } = payload
      return {
        ...state,
        files: state.files.map((file) => {
          console.log({ data, section: file.section })
          const dataFile = getFile(data, file.section)
          if (dataFile) {
            return dataFile
          } else return file
        }),
      }
    }
    case CLEAR_FILE: {
      const { section } = payload
      const updatedFiles = getUpdatedFiles(null, state, null, section, null)
      return { ...state, files: updatedFiles }
    }
    case SET_FILE_ERROR: {
      const { error, section } = payload
      const updatedFiles = getUpdatedFiles(
        null,
        state,
        null,
        section,
        null,
        null,
        error
      )
      return { ...state, files: updatedFiles }
    }
    case CLEAR_ERROR: {
      const { section } = payload
      const file = getFile(state.files, section)
      const updatedFiles = getUpdatedFiles(
        file,
        state,
        file.fileName,
        section,
        file.uuid,
        file.fileType
      )
      return { ...state, files: updatedFiles }
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
    default:
      return state
  }
}

export default reports
