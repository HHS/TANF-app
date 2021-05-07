import {
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  CLEAR_ERROR,
  SET_YEAR,
  SET_FILE_LIST,
  END_FILE_DOWNLOAD,
  START_FILE_DOWNLOAD,
  DOWNLOAD_DIALOG_OPEN,
  SET_SELECTED_YEAR,
  SET_SELECTED_STT,
} from '../actions/reports'

const getFileIndex = (files, section) =>
  files.findIndex((currentFile) => currentFile.section === section)
const getFile = (files, section) =>
  files.find((currentFile) => currentFile.section === section)
export const getUpdatedFiles = (
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
  files: [
    {
      section: 'Active Case Data',
      fileName: null,
      error: null,
      uuid: null,
      fileType: null,
    },
    {
      section: 'Closed Case Data',
      fileName: null,
      error: null,
      uuid: null,
      fileType: null,
    },
    {
      section: 'Aggregate Data',
      fileName: null,
      error: null,
      uuid: null,
      fileType: null,
    },
    {
      section: 'Stratum Data',
      fileName: null,
      error: null,
      uuid: null,
      fileType: null,
    },
  ],
  year: '',
  stt: '',
}

const reports = (state = initialState, action) => {
  const { type, payload = {} } = action
  switch (type) {
    case SET_FILE: {
      const { fileName, section, uuid, fileType } = payload
      const updatedFiles = getUpdatedFiles(
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
          const dataFile = getFile(data, file.section)
          if (dataFile) {
            return dataFile
          } else return file
        }),
      }
    }
    case CLEAR_FILE: {
      const { section } = payload
      const updatedFiles = getUpdatedFiles(state, null, section, null)
      return { ...state, files: updatedFiles }
    }
    case SET_FILE_ERROR: {
      const { error, section } = payload
      const updatedFiles = getUpdatedFiles(
        state,
        null,
        section,
        null,
        null,
        error
      )
      return { ...initialState, files: updatedFiles }
    }
    case CLEAR_ERROR: {
      const { section } = payload
      const file = getFile(state.files, section)
      const updatedFiles = getUpdatedFiles(
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
    default:
      return state
  }
}

export default reports
