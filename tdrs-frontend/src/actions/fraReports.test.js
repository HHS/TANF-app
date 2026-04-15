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
  getFraSubmissionStatus,
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

    it('downloads file on success', async () => {
      const store = mockStore()
      const blob = new Blob(['file-content'])

      get.mockResolvedValue({
        data: blob,
        ok: true,
        status: 200,
        error: null,
      })

      const mockLink = {
        href: '',
        setAttribute: jest.fn(),
        click: jest.fn(),
      }
      jest.spyOn(document, 'createElement').mockReturnValue(mockLink)
      jest.spyOn(document.body, 'appendChild').mockImplementation(() => {})
      jest.spyOn(document.body, 'removeChild').mockImplementation(() => {})
      window.URL.createObjectURL = jest.fn(() => 'blob:test-url')

      await store.dispatch(
        downloadOriginalSubmission({
          id: 42,
          fileName: 'report.txt',
          year: '2025',
          quarter: 'Q1',
          section: 'Active Case Data',
        })
      )

      expect(get).toHaveBeenCalledWith(
        expect.stringContaining('/data_files/42/download/'),
        { responseType: 'blob' }
      )
      expect(mockLink.setAttribute).toHaveBeenCalledWith(
        'download',
        'report (2025-Q1-Active Case Data).txt'
      )
      expect(mockLink.click).toHaveBeenCalled()
      expect(document.body.removeChild).toHaveBeenCalledWith(mockLink)

      document.createElement.mockRestore()
      document.body.appendChild.mockRestore()
      document.body.removeChild.mockRestore()
    })

    it('logs error when API returns non-ok response', async () => {
      const store = mockStore()
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation()

      get.mockResolvedValue({
        data: null,
        ok: false,
        status: 500,
        error: new Error('Server error'),
      })

      await store.dispatch(
        downloadOriginalSubmission({
          id: 42,
          fileName: 'report.txt',
          year: '2025',
          quarter: 'Q1',
          section: 'Active Case Data',
        })
      )

      expect(consoleSpy).toHaveBeenCalledWith(
        'error downloading file',
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })
  })

  describe('getFraSubmissionStatus', () => {
    it('returns data on success', async () => {
      get.mockResolvedValue({
        data: { status: 'complete' },
        ok: true,
        status: 200,
        error: null,
      })

      const result = await getFraSubmissionStatus(99)

      expect(get).toHaveBeenCalledWith(
        expect.stringContaining('/data_files/99/')
      )
      expect(result).toEqual({ data: { status: 'complete' }, ok: true })
    })

    it('throws error on non-ok response', async () => {
      const mockError = new Error('Not found')
      get.mockResolvedValue({
        data: null,
        ok: false,
        status: 404,
        error: mockError,
      })

      await expect(getFraSubmissionStatus(99)).rejects.toThrow('Not found')
    })
  })
})
