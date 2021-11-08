import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { v4 as uuidv4 } from 'uuid'

import {
  SET_SELECTED_YEAR,
  START_FILE_DOWNLOAD,
  SET_FILE,
  SET_FILE_LIST,
  FILE_DOWNLOAD_ERROR,
  DOWNLOAD_DIALOG_OPEN,
  SET_FILE_ERROR,
  SET_SELECTED_STT,
  SET_SELECTED_QUARTER,
  setQuarter,
  setStt,
  setYear,
  upload,
  download,
  getAvailableFileList,
  submit,
  SET_FILE_SUBMITTED,
} from './reports'

describe('actions/reports', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_FILE', async () => {
    const store = mockStore()

    await store.dispatch(
      upload({
        file: { name: 'HELLO', type: 'text/plain' },
        section: 'Active Case Data',
      })
    )

    const actions = store.getActions()

    const { uuid } = actions[0].payload

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({
      file: { name: 'HELLO', type: 'text/plain' },
      fileName: 'HELLO',
      fileType: 'text/plain',
      section: 'Active Case Data',
      uuid,
    })
  })

  it('should dispatch SET_FILE_ERROR when there is an error with the post', async () => {
    const store = mockStore()

    await store.dispatch(
      upload({ boop: 'asdasd', section: 'Active Case Data' })
    )

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE_ERROR)
    expect(actions[0].payload).toHaveProperty(
      'error',
      TypeError("Cannot read property 'name' of undefined")
    )
  })

  it('should dispatch OPEN_FILE_DIALOG when a file has been successfully downloaded', async () => {
    window.URL.createObjectURL = jest.fn(() => null)
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        data: 'Some text',
      })
    )
    const store = mockStore()

    await store.dispatch(
      download({
        id: 1,
        section: 'Active Case Data',
      })
    )
    const actions = store.getActions()

    expect(actions[0].type).toBe(START_FILE_DOWNLOAD)
    try {
      expect(actions[1].type).toBe(DOWNLOAD_DIALOG_OPEN)
    } catch (err) {
      throw actions[1].payload.error
    }
  })

  it('should dispatch SET_FILE_LIST', async () => {
    axios.get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [
          {
            fileName: 'test.txt',
            section: 'Active Case Data',
            uuid: uuidv4(),
          },
          {
            fileName: 'testb.txt',
            section: 'Closed Case Data',
            uuid: uuidv4(),
          },
        ],
      })
    )
    const store = mockStore()

    await store.dispatch(
      getAvailableFileList({
        stt: { id: 10 },
        year: 2020,
      })
    )
    const actions = store.getActions()
    try {
      expect(actions[1].type).toBe(SET_FILE_LIST)
    } catch (err) {
      throw actions[1].payload.error
    }
  })

  it('should dispatch SET_FILE_SUBMITTED', async () => {
    const uuid = uuidv4()
    axios.post.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          extension: 'txt',
          id: 1,
          original_filename: 'Test.txt',
          quarter: 'Q1',
          section: 'Stratum Data',
          slug: uuid,
          year: 2021,
        },
      })
    )
    const store = mockStore()

    await store.dispatch(
      submit({
        formattedSections: '4',
        logger: { alert: jest.fn() },
        quarter: 'Q1',
        setLocalAlertState: jest.fn(),
        stt: { id: 10 },
        uploadedFiles: [
          {
            file: { name: 'Test.txt', type: 'text/plain' },
            fileName: 'Test.txt',
            section: 'Stratum Data',
            uuid,
          },
        ],
        user: { id: 1 },
        year: 2021,
      })
    )
    const actions = store.getActions()

    try {
      expect(axios.post).toHaveBeenCalledTimes(1)
      expect(actions[0].type).toBe(SET_FILE_SUBMITTED)
    } catch (err) {
      throw actions[0].payload.error
    }
  })

  it('should dispatch FILE_DOWNLOAD_ERROR if no year is provided to download', async () => {
    const store = mockStore()

    await store.dispatch(
      download({
        section: 'Active Case Data',
      })
    )
    const actions = store.getActions()
    expect(actions[0].type).toBe(FILE_DOWNLOAD_ERROR)
  })

  it('should dispatch SET_SELECTED_YEAR', async () => {
    const store = mockStore()

    await store.dispatch(setYear(2020))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_SELECTED_YEAR)
    expect(actions[0].payload).toStrictEqual({ year: 2020 })
  })

  it('should dispatch SET_SELECTED_STT', async () => {
    const store = mockStore()

    await store.dispatch(setStt('florida'))

    const actions = store.getActions()
    expect(actions[0].type).toBe(SET_SELECTED_STT)
    expect(actions[0].payload).toStrictEqual({
      stt: 'florida',
    })
  })

  it('should dispatch SET_SELECTED_QUARTER', async () => {
    const store = mockStore()

    await store.dispatch(setQuarter('Q2'))

    const actions = store.getActions()
    expect(actions[0].type).toBe(SET_SELECTED_QUARTER)
    expect(actions[0].payload).toStrictEqual({
      quarter: 'Q2',
    })
  })
})
