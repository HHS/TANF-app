import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  setYear,
  SET_SELECTED_YEAR,
  START_FILE_DOWNLOAD,
  SET_FILE,
  FILE_DOWNLOAD_ERROR,
  DOWNLOAD_DIALOG_OPEN,
  SET_FILE_ERROR,
  SET_SELECTED_STT,
  setStt,
  upload,
  download,
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
    const store = mockStore()

    await store.dispatch(
      download({
        year: 2020,
        section: 'Active Case Data',
      })
    )
    const actions = store.getActions()
    expect(actions[0].type).toBe(START_FILE_DOWNLOAD)
  })

  it('should dispatch FILE_DOWNLOAD_ERROR if no year is provided to download',async () => {

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
