import { get, post } from '../fetch-instance'
import { thunk } from 'redux-thunk'
import configureStore from 'redux-mock-store'

import {
  getFraSubmissionHistory,
  SET_IS_LOADING_SUBMISSION_HISTORY,
  SET_FRA_SUBMISSION_HISTORY,
  SET_IS_UPLOADING_FRA_REPORT,
  uploadFraReport,
  downloadOriginalSubmission,
} from './fraReports'

jest.mock('../fetch-instance')

describe('actions/fraReports', () => {
  const mockStore = configureStore([thunk])

  beforeEach(() => {
    get.mockClear()
    post.mockClear()
  })

  describe('getFraSubmissionHistory', () => {
    it('should handle success without callbacks', async () => {
      const store = mockStore()

      get.mockResolvedValue({
        data: { yay: 'we did it' },
        ok: true,
        status: 200,
        error: null,
      })

      await store.dispatch(
        getFraSubmissionHistory({
          stt: { id: 'stt' },
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

      expect(get).toHaveBeenCalledTimes(1)
    })

    it('should handle fail without callbacks', async () => {
      const store = mockStore()

      get.mockResolvedValue({
        data: null,
        ok: false,
        status: 400,
        error: new Error('Mock fail response'),
      })

      await store.dispatch(
        getFraSubmissionHistory({
          stt: { id: 'stt' },
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

      expect(get).toHaveBeenCalledTimes(1)
    })

    it('should call onSuccess', async () => {
      const store = mockStore()

      get.mockResolvedValue({
        data: { yay: 'we did it' },
        ok: true,
        status: 200,
        error: null,
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        getFraSubmissionHistory(
          {
            stt: { id: 'stt' },
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

      expect(get).toHaveBeenCalledTimes(1)

      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledTimes(0)
    })

    it('should call onError', async () => {
      const store = mockStore()

      get.mockResolvedValue({
        data: null,
        ok: false,
        status: 400,
        error: new Error('Mock fail response'),
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        getFraSubmissionHistory(
          {
            stt: { id: 'stt' },
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

      expect(get).toHaveBeenCalledTimes(1)

      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(1)
    })
  })

  describe('uploadFraReport', () => {
    it('should handle success without callbacks', async () => {
      const store = mockStore()

      post.mockResolvedValue({
        data: { yay: 'success' },
        ok: true,
        status: 200,
        error: null,
      })

      await store.dispatch(
        uploadFraReport({
          stt: { id: 'stt' },
          reportType: 'something',
          fiscalQuarter: '1',
          fiscalYear: '2',
          file: { name: 'bytes' },
          user: { id: 'me' },
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

      expect(post).toHaveBeenCalledTimes(1)
      expect(get).toHaveBeenCalledTimes(0)
    })

    it('should handle fail without callbacks', async () => {
      const store = mockStore()

      post.mockResolvedValue({
        data: null,
        ok: false,
        status: 400,
        error: new Error('Mock fail response'),
      })

      await store.dispatch(
        uploadFraReport({
          stt: { id: 'stt' },
          reportType: 'something',
          fiscalQuarter: '1',
          fiscalYear: '2',
          file: { name: 'bytes' },
          user: { id: 'me' },
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

      expect(post).toHaveBeenCalledTimes(1)
      expect(get).toHaveBeenCalledTimes(0)
    })

    it('should call onSuccess', async () => {
      const store = mockStore()

      post.mockResolvedValue({
        data: { yay: 'success' },
        ok: true,
        status: 200,
        error: null,
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        uploadFraReport(
          {
            stt: { id: 'stt' },
            reportType: 'something',
            fiscalQuarter: '1',
            fiscalYear: '2',
            file: { name: 'bytes' },
            user: { id: 'me' },
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

      expect(post).toHaveBeenCalledTimes(1)
      expect(get).toHaveBeenCalledTimes(0)

      expect(onSuccess).toHaveBeenCalledTimes(1)
      expect(onError).toHaveBeenCalledTimes(0)
    })

    it('should call onError', async () => {
      const store = mockStore()

      post.mockResolvedValue({
        data: null,
        ok: false,
        status: 400,
        error: new Error('Mock fail response'),
      })

      const onSuccess = jest.fn()
      const onError = jest.fn()

      await store.dispatch(
        uploadFraReport(
          {
            stt: { id: 'stt' },
            reportType: 'something',
            fiscalQuarter: '1',
            fiscalYear: '2',
            file: { name: 'bytes' },
            user: { id: 'me' },
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

      expect(post).toHaveBeenCalledTimes(1)
      expect(get).toHaveBeenCalledTimes(0)

      expect(onSuccess).toHaveBeenCalledTimes(0)
      expect(onError).toHaveBeenCalledTimes(1)
    })
  })

  describe('downloadOriginalSubmission', () => {
    it('do nothing if no id provided', async () => {
      const store = mockStore()
      await store.dispatch(downloadOriginalSubmission({}))
      const actions = store.getActions()
      expect(actions.length).toEqual(0)
    })
  })
})
