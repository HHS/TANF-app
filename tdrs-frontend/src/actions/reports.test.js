import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import { upload, SET_FILE, setYear, SET_YEAR } from './reports'

describe('actions/reports.js', () => {
  // Init a mock store to test redux actions
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
})

describe('actions/setYear', () => {
  const mockStore = configureStore([thunk])

  it('should dispatch SET_YEAR', async () => {
    const store = mockStore()

    await store.dispatch(setYear(2020))

    const actions = store.getActions()

    expect(actions[0].type).toBe(SET_YEAR)
    expect(actions[0].payload).toStrictEqual({ year: 2020 })
  })
})
