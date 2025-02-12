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

      expect(actions[1].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[1].payload).toStrictEqual({
        isUploadingFraReport: false,
      })

      expect(actions[2].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[2].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
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

      expect(actions[1].type).toBe(SET_IS_UPLOADING_FRA_REPORT)
      expect(actions[1].payload).toStrictEqual({
        isUploadingFraReport: false,
      })

      expect(actions[2].type).toBe(SET_IS_LOADING_SUBMISSION_HISTORY)
      expect(actions[2].payload).toStrictEqual({
        isLoadingSubmissionHistory: true,
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
})
