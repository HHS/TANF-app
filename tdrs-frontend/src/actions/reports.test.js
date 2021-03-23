import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import { setYear, SET_SELECTED_YEAR, SET_SELECTED_STT, setStt } from './reports'

describe('actions/reports', () => {
  const mockStore = configureStore([thunk])

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
