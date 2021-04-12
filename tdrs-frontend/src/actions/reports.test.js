import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  SET_SELECTED_YEAR,
  SET_FILE,
  SET_SELECTED_STT,
  SET_SELECTED_QUARTER,
  setQuarter,
  setStt,
  setYear,
  upload,
} from './reports'

describe('actions/reports', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_FILE', async () => {
    const store = mockStore()

    await store.dispatch(
      upload({ file: { name: 'HELLO' }, section: 'Active Case Data' })
    )

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_FILE)
    expect(actions[0].payload).toStrictEqual({
      fileName: 'HELLO',
      section: 'Active Case Data',
    })
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
