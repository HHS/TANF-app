import thunk from 'redux-thunk'
import configureStore from 'redux-mock-store'

import { setYear, SET_YEAR } from './upload'

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
