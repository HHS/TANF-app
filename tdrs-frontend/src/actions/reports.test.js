import axios from 'axios'
import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { v4 as uuidv4 } from 'uuid'

import {
  setYear,
  SET_SELECTED_YEAR,
  START_FILE_DOWNLOAD,
  SET_FILE,
  SET_FILE_LIST,
  FILE_DOWNLOAD_ERROR,
  DOWNLOAD_DIALOG_OPEN,
  SET_FILE_ERROR,
  SET_SELECTED_STT,
  setStt,
  upload,
  download,
  getAvailableFileList,
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
    expect(actions[0].payload).toStrictEqual({
      error: Error({ message: 'something went wrong' }),
      section: 'Active Case Data',
    })
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
        year: 2020,
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
})
