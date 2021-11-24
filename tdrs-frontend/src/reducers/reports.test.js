import { v4 as uuidv4 } from 'uuid'
import reducer, { getUpdatedFiles } from './reports'
import {
  CLEAR_ERROR,
  SET_FILE,
  CLEAR_FILE,
  SET_FILE_ERROR,
  SET_SELECTED_YEAR,
  SET_SELECTED_STT,
  SET_FILE_LIST,
  SET_SELECTED_QUARTER,
  SET_FILE_SUBMITTED,
} from '../actions/reports'

const initialState = {
  files: [
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
            },
          ],
        },
      })
    ).toEqual({
      files: [
        {
          fileName: 'test.txt',
          fileType: 'txt',
          id: 1,
          section: 'Active Case Data',
          quarter: 'Q1',
          year: 2021,
          uuid,
        },
        {
          section: 'Closed Case Data',
          uuid: null,
          fileType: null,
          fileName: null,
          error: null,
        },
        {
          section: 'Aggregate Data',
          uuid: null,
          fileType: null,
          fileName: null,
          error: null,
        },
        {
          section: 'Stratum Data',
          uuid: null,
          fileType: null,
          fileName: null,
          error: null,
        },
      ],
      quarter: '',
      stt: '',
      year: '',
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
      files: [
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
      files: [
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
      files: [
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
      files: [
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
    })
  })

  it('should handle CLEAR_ERROR', () => {
    const fakeError = new Error({ message: 'something went wrong' })
    expect(
      reducer(
        {
          files: [
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
      files: [
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
        },
      })
    ).toEqual({
      files: initialState.files,
      year: '',
      stt: 'florida',
      quarter: '',
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
      year: '',
      stt: '',
      quarter: 'Q1',
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
      year: '',
      stt: '',
      quarter: 'Q2',
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
      year: '',
      stt: '',
      quarter: 'Q3',
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
      year: '',
      stt: '',
      quarter: 'Q4',
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
      year: '2021',
      stt: '',
      quarter: '',
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
