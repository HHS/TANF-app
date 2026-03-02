import { get } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  fetchSttList,
  FETCH_STTS,
  SET_STTS,
  SET_STTS_ERROR,
  CLEAR_STTS,
} from './sttList'

jest.mock('../fetch-instance')

describe('actions/stts.js', () => {
  const mockStore = configureStore([thunk])

  it('fetches a list of stts, when the user is authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [{ id: 1, type: 'state', code: 'AL', name: 'Alabama' }],
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS)
    expect(actions[1].payload.data).toStrictEqual([
      { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
    ])
  })

  it('fetches a list of stts and puts "Federal Government" as the first option if it exists, when the user is authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: [
          { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
          {
            id: 57,
            type: 'territory',
            code: 'US',
            name: 'Federal Government',
          },
        ],
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS)
    expect(actions[1].payload.data).toStrictEqual([
      {
        id: 57,
        type: 'territory',
        code: 'US',
        name: 'Federal Government',
      },
      { id: 1, type: 'state', code: 'AL', name: 'Alabama' },
    ])
  })

  it('clears the stt state, if user is not authenticated', async () => {
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: true,
        status: 200,
        error: null,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(CLEAR_STTS)
  })

  it('dispatches an error to the store if the API errors', async () => {
    const mockError = new Error('something went wrong')
    get.mockImplementationOnce(() =>
      Promise.resolve({
        data: null,
        ok: false,
        status: 500,
        error: mockError,
      })
    )
    const store = mockStore()

    await store.dispatch(fetchSttList())

    const actions = store.getActions()
    expect(actions[0].type).toBe(FETCH_STTS)
    expect(actions[1].type).toBe(SET_STTS_ERROR)
    expect(actions[1].payload).toStrictEqual({
      error: mockError,
    })
  })
})
