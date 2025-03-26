import axios from 'axios'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'
import { v4 as uuidv4 } from 'uuid'

import {
  getFraSubmissionHistory,
  upload,
  SET_IS_LOADING_SUBMISSION_HISTORY,
  SET_FRA_SUBMISSION_HISTORY,
  SET_IS_UPLOADING_FRA_REPORT,
  uploadFraReport,
  pollFraSubmissionStatus,
  SET_IS_LOADING_FRA_SUBMISSION_STATUS,
  SET_FRA_SUBMISSION_STATUS,
} from './fraReports'

describe('actions/fraReports', () => {
  jest.mock('axios')
  const mockAxios = axios
  const mockStore = configureStore([thunk])

  describe('getFraSubmissionHistory', () => {
    it('should handle success without callbacks', async () => {
      const store = mockStore()

      mockAxios.get.mockResolvedValue({
        data: { yay: 'we did it' },
      })

      await store.dispatch(
        getFraSubmissionHistory({
          stt: 'stt',
          reportType: 'something',
          fiscalQuarter: '1',
          fiscalYear: '2',
        })
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(3)

      expect(actions[0].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[0].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
      })

      expect(actions[1].type).toBe(SET_FRA_SUBMISSION_HISTORY)
      expect(actions[1].payload).toStrictEqual({
        submissionHistory: { yay: 'we did it' },
      })

      expect(actions[2].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[2].payload).toStrictEqual({
        isLoadingSubmissionHistory: false,
      })

      expect(axios.get).toHaveBeenCalledTimes(1)
    })

    it('should handle fail without callbacks', async () => {
      const store = mockStore()

      mockAxios.get.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      await store.dispatch(
        getFraSubmissionHistory({
          stt: 'stt',
          reportType: 'something',
          fiscalQuarter: '1',
          fiscalYear: '2',
        })
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(2)

      expect(actions[0].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[0].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[1].payload).toStrictEqual({
        isLoadingSubmissionHistory: false,
      })

      expect(axios.get).toHaveBeenCalledTimes(1)
    })

    it('should call onSuccess', async () => {
      const store = mockStore()

      mockAxios.get.mockResolvedValue({
        data: { yay: 'we did it' },
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        getFraSubmissionHistory(
          {
            stt: 'stt',
            reportType: 'something',
            fiscalQuarter: '1',
            fiscalYear: '2',
          },
          onSuccess,
          onError
        )
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(3)

      expect(actions[0].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[0].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
      })

      expect(actions[1].type).toBe(SET_FRA_SUBMISSION_HISTORY)
      expect(actions[1].payload).toStrictEqual({
        submissionHistory: { yay: 'we did it' },
      })

      expect(actions[2].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[2].payload).toStrictEqual({
        isLoadingSubmissionHistory: false,
      })

      expect(axios.get).toHaveBeenCalledTimes(1)

      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledTimes(0)
    })

    it('should call onError', async () => {
      const store = mockStore()

      mockAxios.get.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        getFraSubmissionHistory(
          {
            stt: 'stt',
            reportType: 'something',
            fiscalQuarter: '1',
            fiscalYear: '2',
          },
          onSuccess,
          onError
        )
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(2)

      expect(actions[0].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[0].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[1].payload).toStrictEqual({
        isLoadingSubmissionHistory: false,
      })

      expect(axios.get).toHaveBeenCalledTimes(1)

      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(1)
    })
  })

  describe('uploadFraReport', () => {
    it('should handle success without callbacks', async () => {
      const store = mockStore()

      mockAxios.post.mockResolvedValue({
        data: { yay: 'success' },
      })

      mockAxios.get.mockResolvedValue({
        data: { yay: 'we did it' },
      })

      await store.dispatch(
        uploadFraReport({
          stt: 'stt',
          reportType: 'something',
          fiscalQuarter: '1',
          fiscalYear: '2',
          file: 'bytes',
          user: 'me',
        })
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(3)

      expect(actions[0].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[0].payload).toStrictEqual({
        isUploadingFraReport: true,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[1].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
      })

      expect(actions[2].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[2].payload).toStrictEqual({
        isUploadingFraReport: false,
      })

      expect(axios.post).toHaveBeenCalledTimes(1)
      expect(axios.get).toHaveBeenCalledTimes(1)
    })

    it('should handle fail without callbacks', async () => {
      const store = mockStore()

      mockAxios.post.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      mockAxios.get.mockResolvedValue({
        data: { yay: 'we did it' },
      })

      await store.dispatch(
        uploadFraReport({
          stt: 'stt',
          reportType: 'something',
          fiscalQuarter: '1',
          fiscalYear: '2',
          file: 'bytes',
          user: 'me',
        })
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(2)

      expect(actions[0].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[0].payload).toStrictEqual({
        isUploadingFraReport: true,
      })

      expect(actions[1].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[1].payload).toStrictEqual({
        isUploadingFraReport: false,
      })

      expect(axios.post).toHaveBeenCalledTimes(1)
      expect(axios.get).toHaveBeenCalledTimes(0)
    })

    it('should call onSuccess', async () => {
      const store = mockStore()

      mockAxios.post.mockResolvedValue({
        data: { yay: 'success' },
      })

      mockAxios.get.mockResolvedValue({
        data: { yay: 'we did it' },
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        uploadFraReport(
          {
            stt: 'stt',
            reportType: 'something',
            fiscalQuarter: '1',
            fiscalYear: '2',
            file: 'bytes',
            user: 'me',
          },
          onSuccess,
          onError
        )
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(3)

      expect(actions[0].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[0].payload).toStrictEqual({
        isUploadingFraReport: true,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[1].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
      })

      expect(actions[2].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[2].payload).toStrictEqual({
        isUploadingFraReport: false,
      })

      expect(axios.post).toHaveBeenCalledTimes(1)
      expect(axios.get).toHaveBeenCalledTimes(1)

      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledTimes(0)
    })

    it('should call onError', async () => {
      const store = mockStore()

      mockAxios.post.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      mockAxios.get.mockResolvedValue({
        data: { yay: 'we did it' },
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        uploadFraReport(
          {
            stt: 'stt',
            reportType: 'something',
            fiscalQuarter: '1',
            fiscalYear: '2',
            file: 'bytes',
            user: 'me',
          },
          onSuccess,
          onError
        )
      )

      const actions = store.getActions()

      expect(actions.length).toEqual(2)

      expect(actions[0].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[0].payload).toStrictEqual({
        isUploadingFraReport: true,
      })

      expect(actions[1].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[1].payload).toStrictEqual({
        isUploadingFraReport: false,
      })

      expect(axios.post).toHaveBeenCalledTimes(1)
      expect(axios.get).toHaveBeenCalledTimes(0)

      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(1)
    })
  })

  describe('pollFraSubmissionStatus', () => {
    it('should not call retry if success received', async () => {
      const store = mockStore()

      const test = jest.fn(() => true)
      const retry = jest.fn()
      const onSuccess = jest.fn()
      const onError = jest.fn()

      mockAxios.get.mockResolvedValue({
        data: { id: 1, hasErrors: true, summary: { status: 'Approved' } },
      })

      await store.dispatch(
        pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
      )

      const actions = store.getActions()
      expect(actions.length).toEqual(4)

      expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[0].payload).toStrictEqual({
        datafile_id: 1,
        tryNumber: 1,
        isPerformingRequest: true,
        isDone: false,
        error: null,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[1].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
      })

      expect(actions[2].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[2].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
        isDone: true,
        error: null,
      })

      expect(actions[3].type).toBe(SET_FRA_SUBMISSION_STATUS)
      expect(actions[3].payload).toStrictEqual({
        datafile_id: 1,
        datafile: {
          id: 1,
          hasErrors: true,
          summary: { status: 'Approved' },
        },
      })

      expect(test).toHaveBeenCalledTimes(1)
      expect(retry).toHaveBeenCalledTimes(0)
      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledTimes(0)
    })

    it('calls retry until a success is received', async () => {
      const store = mockStore()

      let test = jest.fn((f) => f?.summary?.status !== 'Pending')
      const retry = jest.fn()
      const onSuccess = jest.fn()
      const onError = jest.fn()

      mockAxios.get.mockResolvedValue({
        data: { summary: { status: 'Pending' } },
      })

      await store.dispatch(
        pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
      )

      let actions = store.getActions()
      expect(actions.length).toEqual(2)

      expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[0].payload).toStrictEqual({
        datafile_id: 1,
        tryNumber: 1,
        isPerformingRequest: true,
        isDone: false,
        error: null,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[1].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
      })

      expect(test).toHaveBeenCalledTimes(1)
      expect(retry).toHaveBeenCalledTimes(1)
      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(0)

      await store.dispatch(
        pollFraSubmissionStatus(1, 2, test, retry, onSuccess, onError)
      )

      actions = store.getActions()
      expect(actions.length).toEqual(4)

      expect(actions[2].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[2].payload).toStrictEqual({
        datafile_id: 1,
        tryNumber: 2,
        isPerformingRequest: true,
        isDone: false,
        error: null,
      })

      expect(actions[3].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[3].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
      })

      expect(test).toHaveBeenCalledTimes(2)
      expect(retry).toHaveBeenCalledTimes(2)
      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(0)

      mockAxios.get.mockResolvedValue({
        data: { id: 1, hasErrors: true, summary: { status: 'Approved' } },
      })

      await store.dispatch(
        pollFraSubmissionStatus(1, 3, test, retry, onSuccess, onError)
      )

      actions = store.getActions()
      expect(actions.length).toEqual(8)

      expect(actions[4].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[4].payload).toStrictEqual({
        datafile_id: 1,
        tryNumber: 3,
        isPerformingRequest: true,
        isDone: false,
        error: null,
      })

      expect(actions[5].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[5].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
      })

      expect(actions[6].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[6].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
        isDone: true,
        error: null,
      })

      expect(actions[7].type).toBe(SET_FRA_SUBMISSION_STATUS)
      expect(actions[7].payload).toStrictEqual({
        datafile_id: 1,
        datafile: {
          id: 1,
          hasErrors: true,
          summary: { status: 'Approved' },
        },
      })

      expect(test).toHaveBeenCalledTimes(3)
      expect(retry).toHaveBeenCalledTimes(2)
      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledTimes(0)
    })

    it('calls onError when a request fails', async () => {
      const store = mockStore()

      const test = jest.fn(() => true)
      const retry = jest.fn()
      const onSuccess = jest.fn()
      const onError = jest.fn()

      mockAxios.get.mockRejectedValue({
        message: 'Error',
        response: {
          status: 400,
          data: { detail: 'Mock fail response' },
        },
      })

      await store.dispatch(
        pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
      )

      const actions = store.getActions()
      expect(actions.length).toEqual(2)

      expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[0].payload).toStrictEqual({
        datafile_id: 1,
        tryNumber: 1,
        isPerformingRequest: true,
        isDone: false,
        error: null,
      })

      expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[1].payload).toStrictEqual({
        datafile_id: 1,
        isPerformingRequest: false,
        isDone: true,
        error: {
          message: 'Error',
          response: {
            status: 400,
            data: { detail: 'Mock fail response' },
          },
        },
      })

      expect(test).toHaveBeenCalledTimes(0)
      expect(retry).toHaveBeenCalledTimes(0)
      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(1)
    })

    it('calls onError when tryNumber > MAX_TRIES', async () => {
      const store = mockStore()

      const test = jest.fn(() => true)
      const retry = jest.fn()
      const onSuccess = jest.fn()
      const onError = jest.fn()

      mockAxios.get.mockResolvedValue({
        data: { id: 1, hasErrors: true, summary: { status: 'Approved' } },
      })

      await store.dispatch(
        pollFraSubmissionStatus(1, 31, test, retry, onSuccess, onError)
      )

      const actions = store.getActions()
      expect(actions.length).toEqual(1)

      expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
      expect(actions[0].payload).toEqual({
        datafile_id: 1,
        isPerformingRequest: false,
        isDone: true,
        error: new Error(
          'Exceeded max number of tries to update submission status.'
        ),
      })

      expect(test).toHaveBeenCalledTimes(0)
      expect(retry).toHaveBeenCalledTimes(0)
      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(1)
    })
  })
})
