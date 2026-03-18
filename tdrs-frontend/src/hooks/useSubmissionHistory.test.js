import React from 'react'
import { render, waitFor } from '@testing-library/react'
import configureMockStore from 'redux-mock-store'
import { Provider } from 'react-redux'
import { thunk } from 'redux-thunk'

import { useSubmissionHistory } from './useSubmissionHistory'
import { SET_TANF_SUBMISSION_STATUS } from '../actions/reports'

const mockContext = {
  isPolling: {},
  startPolling: jest.fn(),
}

jest.mock('../components/Reports/ReportsContext', () => ({
  useReportsContext: () => mockContext,
}))

const mockStore = configureMockStore([thunk])

const renderWithStore = (store, filterValues) => {
  const TestComponent = () => {
    useSubmissionHistory(filterValues)
    return null
  }

  const renderResult = render(
    <Provider store={store}>
      <TestComponent />
    </Provider>
  )

  return { ...renderResult, TestComponent }
}

describe('useSubmissionHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockContext.isPolling = {}
  })

  it('restarts polling for pending files when history loads', async () => {
    const pendingFile = { id: 1, summary: { status: 'Pending' } }
    const completedFile = { id: 2, summary: { status: 'Approved' } }
    const store = mockStore({
      reports: {
        files: [pendingFile, completedFile],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledWith(
        `${pendingFile.id}`,
        expect.any(Function),
        expect.any(Function),
        expect.any(Function),
        expect.any(Function),
        expect.any(Function)
      )
    })
  })

  it('does not restart polling when already polling a file', async () => {
    const pendingFile = { id: 3, summary: { status: 'Pending' } }
    mockContext.isPolling = { 3: true }
    const store = mockStore({
      reports: {
        files: [pendingFile],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).not.toHaveBeenCalled()
    })
  })

  it('does not restart polling when isPolling changes without new files', async () => {
    const pendingFile = { id: 4, summary: { status: 'Pending' } }
    const store = mockStore({
      reports: {
        files: [pendingFile],
        loading: false,
      },
    })

    const renderResult = renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })

    mockContext.isPolling = { 4: true }
    renderResult.rerender(
      <Provider store={store}>
        <renderResult.TestComponent />
      </Provider>
    )

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })
  })

  it('does not fetch file list on first render when polling has not started', async () => {
    mockContext.isPolling = { 1: false }
    const store = mockStore({
      reports: {
        files: [],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(store.getActions()).toEqual([])
      expect(mockContext.startPolling).not.toHaveBeenCalled()
    })
  })

  it('uses polling callbacks to determine completion and dispatch status updates', async () => {
    const pendingFile = { id: 9, summary: { status: 'Pending' } }
    const store = mockStore({
      reports: {
        files: [pendingFile],
        loading: false,
      },
    })

    renderWithStore(store, {
      quarter: 'Q1',
      stt: { id: 1 },
      year: '2021',
      file_type: 'test',
    })

    await waitFor(() => {
      expect(mockContext.startPolling).toHaveBeenCalledTimes(1)
    })

    const [, fetchStatusAction, shouldStopPolling, handleSuccess] =
      mockContext.startPolling.mock.calls[0]

    expect(typeof fetchStatusAction()).toBe('object')
    expect(
      shouldStopPolling({ data: { summary: { status: 'Pending' } } })
    ).toBe(false)
    expect(
      shouldStopPolling({ data: { summary: { status: 'Accepted' } } })
    ).toBe(true)
    expect(shouldStopPolling({ data: {} })).toBeUndefined()

    const response = {
      data: { id: pendingFile.id, summary: { status: 'Accepted' } },
    }
    handleSuccess(response)

    expect(store.getActions()).toContainEqual({
      type: SET_TANF_SUBMISSION_STATUS,
      payload: {
        datafile_id: pendingFile.id,
        datafile: response.data,
      },
    })
  })
})
