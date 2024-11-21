import { v4 as uuidv4 } from 'uuid'
import reducer, { defaultFileUploadSections, getUpdatedFiles } from './reports'
import {
  CLEAR_ERROR,
  SET_FILE,
  CLEAR_FILE,
  FILE_EXT_ERROR,
  SET_FILE_ERROR,
  SET_SELECTED_YEAR,
  SET_SELECTED_STT,
  SET_FILE_LIST,
  SET_SELECTED_QUARTER,
  SET_FILE_SUBMITTED,
} from '../actions/reports'

const initialState = {
  files: [],
  fileUploadSections: defaultFileUploadSections,
  submittedFiles: [
    {
      section: 'Active Case Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
    {
      section: 'Closed Case Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
    {
      section: 'Aggregate Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
    {
      section: 'Stratum Data',
      fileName: null,
      fileType: null,
      error: null,
      uuid: null,
    },
  ],
  isLoadingCurrentSubmission: false,
  currentSubmissionError: null,
  year: '',
  stt: '',
  quarter: '',
  fileType: 'tanf',
}

describe('reducers/reports', () => {
  it('should return the initial state', () => {
    expect(reducer(undefined, {})).toEqual(initialState)
  })

  it('should handle SET_FILE_LIST', () => {
    const uuid = uuidv4()
    expect(
      reducer(undefined, {
        type: SET_FILE_LIST,
        payload: {
          data: [
            {
              id: 1,
              extension: 'txt',
              original_filename: 'test.txt',
              section: 'Active Case Data',
              quarter: 'Q1',
              slug: uuid,
              year: 2021,
              submitted_by: 'test@test.com',
            },
          ],
        },
      })
    ).toEqual({
      submittedFiles: initialState.submittedFiles,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      fileUploadSections: initialState.fileUploadSections,
      files: [
        {
          fileName: 'test.txt',
          fileType: 'txt',
          id: 1,
          section: 'Active Case Data',
          quarter: 'Q1',
          year: 2021,
          submittedBy: 'test@test.com',
          uuid,
        },
      ],
      quarter: '',
      stt: '',
      year: '',
      fileType: 'tanf',
    })
  })

  it('should handle SET_FILE', () => {
    const uuid = uuidv4()
    expect(
      reducer(undefined, {
        type: SET_FILE,
        payload: {
          file: {},
          fileName: 'Test.txt',
          fileType: 'text/plain',
          section: 'Stratum Data',
          uuid,
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      fileUploadSections: initialState.fileUploadSections,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: {},
          fileName: 'Test.txt',
          fileType: 'text/plain',
          id: null,
          error: null,
          uuid,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: 'tanf',
    })
  })

  it('should handle SET_FILE_SUBMITTED', () => {
    const uuid = uuidv4()
    expect(
      reducer(undefined, {
        type: SET_FILE_SUBMITTED,
        payload: {
          submittedFile: {
            extension: 'txt',
            id: 1,
            original_filename: 'Test.txt',
            quarter: 'Q1',
            section: 'Stratum Data',
            slug: uuid,
            year: 2021,
          },
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      fileUploadSections: initialState.fileUploadSections,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          fileName: 'Test.txt',
          fileType: 'txt',
          id: 1,
          quarter: 'Q1',
          year: 2021,
          uuid,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: 'tanf',
    })
  })

  it('should handle CLEAR_FILE', () => {
    expect(
      reducer(undefined, {
        type: CLEAR_FILE,
        payload: {
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      fileUploadSections: initialState.fileUploadSections,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
          fileName: undefined,
          fileType: null,
          id: null,
          error: null,
          uuid: null,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: 'tanf',
    })
  })

  it('should handle FILE_EXT_ERROR', () => {
    expect(
      reducer(undefined, {
        type: FILE_EXT_ERROR,
        payload: {
          error: { message: 'Test invalid ext.' },
          section: 'Active Case Data',
        },
      })
    ).toEqual({
      ...initialState,
      submittedFiles: [
        {
          id: null,
          file: null,
          section: 'Active Case Data',
          fileName: undefined,
          error: { message: 'Test invalid ext.' },
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
    })
  })

  it('should handle SET_FILE_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(undefined, {
        type: SET_FILE_ERROR,
        payload: {
          error: fakeError,
          section: 'Stratum Data',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      fileUploadSections: initialState.fileUploadSections,
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
          fileName: undefined,
          fileType: null,
          id: null,
          error: fakeError,
          uuid: null,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: 'tanf',
    })
  })

  it('should handle CLEAR_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(
        {
          submittedFiles: [
            {
              section: 'Active Case Data',
              fileName: null,
              fileType: null,
              error: null,
              uuid: null,
            },
            {
              section: 'Closed Case Data',
              fileName: null,
              fileType: null,
              error: null,
              uuid: null,
            },
            {
              section: 'Aggregate Data',
              fileName: null,
              fileType: null,
              error: null,
              uuid: null,
            },
            {
              section: 'Stratum Data',
              fileName: null,
              fileType: null,
              error: fakeError,
              uuid: null,
            },
          ],
          stt: '',
          quarter: '',
          year: '2020',
        },
        {
          type: CLEAR_ERROR,
          payload: {
            section: 'Stratum Data',
          },
        }
      )
    ).toEqual({
      submittedFiles: [
        {
          section: 'Active Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Closed Case Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Aggregate Data',
          fileName: null,
          fileType: null,
          error: null,
          uuid: null,
        },
        {
          section: 'Stratum Data',
          file: null,
          fileName: null,
          fileType: null,
          id: null,
          error: null,
          uuid: null,
        },
      ],
      stt: '',
      quarter: '',
      year: '2020',
    })
  })

  it('should handle "SET_SELECTED_STT"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_STT,
        payload: {
          stt: 'florida',
          newUploadSections: [],
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      submittedFiles: initialState.submittedFiles,
      fileUploadSections: [],
      year: '',
      stt: 'florida',
      quarter: '',
      fileType: 'tanf',
    })
  })

  it('should handle "SET_SELECTED_QUARTER"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_QUARTER,
        payload: {
          quarter: 'Q1',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      submittedFiles: initialState.submittedFiles,
      fileUploadSections: initialState.fileUploadSections,
      year: '',
      stt: '',
      quarter: 'Q1',
      fileType: 'tanf',
    })

    expect(
      reducer(undefined, {
        type: SET_SELECTED_QUARTER,
        payload: {
          quarter: 'Q2',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      submittedFiles: initialState.submittedFiles,
      fileUploadSections: initialState.fileUploadSections,
      year: '',
      stt: '',
      quarter: 'Q2',
      fileType: 'tanf',
    })

    expect(
      reducer(undefined, {
        type: SET_SELECTED_QUARTER,
        payload: {
          quarter: 'Q3',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      submittedFiles: initialState.submittedFiles,
      fileUploadSections: initialState.fileUploadSections,
      year: '',
      stt: '',
      quarter: 'Q3',
      fileType: 'tanf',
    })
    expect(
      reducer(undefined, {
        type: SET_SELECTED_QUARTER,
        payload: {
          quarter: 'Q4',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      submittedFiles: initialState.submittedFiles,
      fileUploadSections: initialState.fileUploadSections,
      year: '',
      stt: '',
      quarter: 'Q4',
      fileType: 'tanf',
    })
  })

  it('should handle "SET_SELECTED_YEAR"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_YEAR,
        payload: {
          year: '2021',
        },
      })
    ).toEqual({
      files: initialState.files,
      isLoadingCurrentSubmission: initialState.isLoadingCurrentSubmission,
      currentSubmissionError: initialState.currentSubmissionError,
      submittedFiles: initialState.submittedFiles,
      fileUploadSections: initialState.fileUploadSections,
      year: '2021',
      stt: '',
      quarter: '',
      fileType: 'tanf',
    })
  })

  it('should be able to update files with a new value and return those files', () => {
    const uuid = uuidv4()

    const updatedFiles = getUpdatedFiles({
      state: initialState,
      id: 10,
      file: {},
      fileName: 'Test.txt',
      section: 'Active Case Data',
      fileType: 'text/plain',
      uuid,
    })

    expect(updatedFiles).toStrictEqual([
      {
        file: {},
        section: 'Active Case Data',
        fileName: 'Test.txt',
        fileType: 'text/plain',
        error: null,
        id: 10,
        uuid,
      },
      {
        section: 'Closed Case Data',
        fileName: null,
        fileType: null,
        error: null,
        uuid: null,
      },
      {
        section: 'Aggregate Data',
        fileName: null,
        fileType: null,
        error: null,
        uuid: null,
      },
      {
        section: 'Stratum Data',
        fileName: null,
        fileType: null,
        error: null,
        uuid: null,
      },
    ])
  })
})
