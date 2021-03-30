import {
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  CLEAR_ERROR,
  SET_YEAR,
} from '../actions/reports'

export const getUpdatedFiles = (
  state,
  fileName,
  section,
  uuid = null,
  fileType = null,
  error = null
) => {
  const oldFileIndex = state.files.findIndex(
    (currentFile) => currentFile.section === section
  )
  const updatedFiles = [...state.files]
  updatedFiles[oldFileIndex] = {
    section,
    fileName,
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
  year: 2020,
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
      const updatedFiles = getUpdatedFiles(state, null, section, null)
      return { ...state, files: updatedFiles }
    }
    case SET_YEAR: {
      const { year } = payload
      return { ...state, year }
    }
    default:
      return state
  }
}

export default reports
