import { v4 as uuidv4 } from 'uuid'
import reducer, { getUpdatedFiles } from './reports'
import {
  CLEAR_ERROR,
  SET_FILE,
  CLEAR_FILE,
  FILE_EXT_ERROR,
  SET_FILE_ERROR,
  SET_SELECTED_STT,
  SET_FILE_LIST,
  SET_FILE_SUBMITTED,
} from '../actions/reports'

const initialState = {
  files: [],
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
  year: '',
  stt: '',
  quarter: '',
  fileType: '',
  loading: false,
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
              program_type: 'TAN',
              s3_version_id: 'v123',
              created_at: '2021-01-01T00:00:00Z',
              has_error: false,
              summary: null,
              latest_reparse_file_meta: null,
            },
          ],
        },
      })
    ).toEqual({
      submittedFiles: initialState.submittedFiles,
      files: [
        {
          fileName: 'test.txt',
          fileType: 'txt',
          id: 1,
          section: 'Active Case Data',
          quarter: 'Q1',
          program_type: 'TAN',
          year: 2021,
          submittedBy: 'test@test.com',
          uuid,
          s3_version_id: 'v123',
          createdAt: '2021-01-01T00:00:00Z',
          hasError: false,
          summary: null,
          latest_reparse_file_meta: null,
        },
      ],
      quarter: '',
      stt: '',
      year: '',
      fileType: '',
      loading: false,
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
      fileType: '',
      loading: false,
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
            s3_version_id: 'v456',
            created_at: '2021-02-01T00:00:00Z',
            submitted_by: 'user@test.com',
            has_error: false,
            summary: null,
            latest_reparse_file_meta: null,
          },
        },
      })
    ).toEqual({
      files: initialState.files,
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
          s3_version_id: 'v456',
          createdAt: '2021-02-01T00:00:00Z',
          submittedBy: 'user@test.com',
          hasError: false,
          summary: null,
          latest_reparse_file_meta: null,
        },
      ],
      stt: '',
      year: '',
      quarter: '',
      fileType: '',
      loading: false,
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
      fileType: '',
      loading: false,
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
      fileType: '',
      loading: false,
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
          loading: false,
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
      loading: false,
    })
  })

  it('should handle "SET_SELECTED_STT"', () => {
    expect(
      reducer(undefined, {
        type: SET_SELECTED_STT,
        payload: {
          stt: 'florida',
        },
      })
    ).toEqual({
      files: initialState.files,
      submittedFiles: initialState.submittedFiles,
      year: '',
      stt: 'florida',
      quarter: '',
      fileType: '',
      loading: false,
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
