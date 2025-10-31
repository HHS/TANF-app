import { render, screen, act } from '@testing-library/react'
import { usePollingTimer } from './usePollingTimer'

// Helper component to test the hook
// function TestComponent({ testFn }) {
//   const hookResult = usePollingTimer()
//   testFn(hookResult)
//   return (
//     <div data-testid="isSubmitting">{hookResult.isSubmitting.toString()}</div>
//   )
// }

// describe('usePollingTimer', () => {
//   // it('should initialize with isSubmitting as false', () => {
//   //   let hookResult
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   expect(hookResult.isSubmitting).toBe(false)
//   //   expect(screen.getByTestId('isSubmitting').textContent).toBe('false')
//   // })
//   // it('should set isSubmitting to true when onSubmitStart is called', () => {
//   //   let hookResult
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   act(() => {
//   //     hookResult.onSubmitStart()
//   //   })
//   //   expect(hookResult.isSubmitting).toBe(true)
//   //   expect(screen.getByTestId('isSubmitting').textContent).toBe('true')
//   // })
//   // it('should set isSubmitting to false when onSubmitComplete is called', () => {
//   //   let hookResult
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   // First set it to true
//   //   act(() => {
//   //     hookResult.onSubmitStart()
//   //   })
//   //   // Then set it back to false
//   //   act(() => {
//   //     hookResult.onSubmitComplete()
//   //   })
//   //   expect(hookResult.isSubmitting).toBe(false)
//   //   expect(screen.getByTestId('isSubmitting').textContent).toBe('false')
//   // })
//   // it('should execute the submission function and return its result', async () => {
//   //   let hookResult
//   //   const mockSubmitFn = jest.fn().mockResolvedValue('success')
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   let returnValue
//   //   await act(async () => {
//   //     returnValue = await hookResult.executeSubmission(mockSubmitFn)
//   //   })
//   //   expect(mockSubmitFn).toHaveBeenCalledTimes(1)
//   //   expect(returnValue).toBe('success')
//   //   expect(hookResult.isSubmitting).toBe(false)
//   //   expect(screen.getByTestId('isSubmitting').textContent).toBe('false')
//   // })
//   // it('should call onSuccess callback when submission succeeds', async () => {
//   //   let hookResult
//   //   const mockSubmitFn = jest.fn().mockResolvedValue('success')
//   //   const onSuccess = jest.fn()
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   await act(async () => {
//   //     await hookResult.executeSubmission(mockSubmitFn, { onSuccess })
//   //   })
//   //   expect(onSuccess).toHaveBeenCalledWith('success')
//   //   expect(hookResult.isSubmitting).toBe(false)
//   // })
//   // it('should call onError callback when submission fails', async () => {
//   //   let hookResult
//   //   const error = new Error('Submission failed')
//   //   const mockSubmitFn = jest.fn().mockRejectedValue(error)
//   //   const onError = jest.fn()
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   let promise
//   //   await act(async () => {
//   //     promise = hookResult.executeSubmission(mockSubmitFn, { onError })
//   //     // Need to catch the error to prevent test failure
//   //     try {
//   //       await promise
//   //     } catch (e) {
//   //       // Expected error
//   //     }
//   //   })
//   //   expect(onError).toHaveBeenCalledWith(error)
//   //   expect(hookResult.isSubmitting).toBe(false)
//   // })
//   // it('should re-throw error when submission fails without onError callback', async () => {
//   //   let hookResult
//   //   const mockSubmitFn = jest.fn(() => {
//   //     throw new Error('Submission failed without callback')
//   //   })
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   let promise
//   //   await act(async () => {
//   //     promise = hookResult.executeSubmission(mockSubmitFn)
//   //     try {
//   //       await promise
//   //     } catch (e) {
//   //       expect(e.message).toEqual('Submission failed without callback')
//   //     }
//   //   })
//   //   expect(hookResult.isSubmitting).toBe(false)
//   // })
//   // it('should prevent multiple submissions when isSubmitting is true', async () => {
//   //   let hookResult
//   //   const mockSubmitFn = jest.fn().mockResolvedValue('success')
//   //   render(
//   //     <TestComponent
//   //       testFn={(result) => {
//   //         hookResult = result
//   //       }}
//   //     />
//   //   )
//   //   // Manually set isSubmitting to true
//   //   act(() => {
//   //     hookResult.onSubmitStart()
//   //   })
//   //   // Try to execute submission while already submitting
//   //   act(() => {
//   //     hookResult.executeSubmission(mockSubmitFn)
//   //   })
//   //   // The submit function should not be called
//   //   expect(mockSubmitFn).not.toHaveBeenCalled()
//   // })
//   describe('pollFraSubmissionStatus', () => {
//     it('should not call retry if success received', async () => {
//       const store = mockStore()

//       const test = jest.fn(() => true)
//       const retry = jest.fn()
//       const onSuccess = jest.fn()
//       const onError = jest.fn()

//       mockAxios.get.mockResolvedValue({
//         data: { id: 1, hasErrors: true, summary: { status: 'Approved' } },
//       })

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
//       )

//       const actions = store.getActions()
//       expect(actions.length).toEqual(4)

//       expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[0].payload).toStrictEqual({
//         datafile_id: 1,
//         tryNumber: 1,
//         isPerformingRequest: true,
//         isDone: false,
//         error: null,
//       })

//       expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[1].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//       })

//       expect(actions[2].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[2].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//         isDone: true,
//         error: null,
//       })

//       expect(actions[3].type).toBe(SET_FRA_SUBMISSION_STATUS)
//       expect(actions[3].payload).toStrictEqual({
//         datafile_id: 1,
//         datafile: {
//           id: 1,
//           hasErrors: true,
//           summary: { status: 'Approved' },
//         },
//       })

//       expect(test).toHaveBeenCalledTimes(1)
//       expect(retry).toHaveBeenCalledTimes(0)
//       expect(onSuccess).toHaveBeenCalledTimes(1)
//       expect(onError).toHaveBeenCalledTimes(0)
//     })

//     it('calls retry until a success is received', async () => {
//       const store = mockStore()

//       let test = jest.fn((f) => f?.summary?.status !== 'Pending')
//       const retry = jest.fn()
//       const onSuccess = jest.fn()
//       const onError = jest.fn()

//       mockAxios.get.mockResolvedValue({
//         data: { summary: { status: 'Pending' } },
//       })

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
//       )

//       let actions = store.getActions()
//       expect(actions.length).toEqual(2)

//       expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[0].payload).toStrictEqual({
//         datafile_id: 1,
//         tryNumber: 1,
//         isPerformingRequest: true,
//         isDone: false,
//         error: null,
//       })

//       expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[1].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//       })

//       expect(test).toHaveBeenCalledTimes(1)
//       expect(retry).toHaveBeenCalledTimes(1)
//       expect(onSuccess).toHaveBeenCalledTimes(0)
//       expect(onError).toHaveBeenCalledTimes(0)

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 2, test, retry, onSuccess, onError)
//       )

//       actions = store.getActions()
//       expect(actions.length).toEqual(4)

//       expect(actions[2].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[2].payload).toStrictEqual({
//         datafile_id: 1,
//         tryNumber: 2,
//         isPerformingRequest: true,
//         isDone: false,
//         error: null,
//       })

//       expect(actions[3].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[3].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//       })

//       expect(test).toHaveBeenCalledTimes(2)
//       expect(retry).toHaveBeenCalledTimes(2)
//       expect(onSuccess).toHaveBeenCalledTimes(0)
//       expect(onError).toHaveBeenCalledTimes(0)

//       mockAxios.get.mockResolvedValue({
//         data: { id: 1, hasErrors: true, summary: { status: 'Approved' } },
//       })

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 3, test, retry, onSuccess, onError)
//       )

//       actions = store.getActions()
//       expect(actions.length).toEqual(8)

//       expect(actions[4].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[4].payload).toStrictEqual({
//         datafile_id: 1,
//         tryNumber: 3,
//         isPerformingRequest: true,
//         isDone: false,
//         error: null,
//       })

//       expect(actions[5].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[5].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//       })

//       expect(actions[6].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[6].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//         isDone: true,
//         error: null,
//       })

//       expect(actions[7].type).toBe(SET_FRA_SUBMISSION_STATUS)
//       expect(actions[7].payload).toStrictEqual({
//         datafile_id: 1,
//         datafile: {
//           id: 1,
//           hasErrors: true,
//           summary: { status: 'Approved' },
//         },
//       })

//       expect(test).toHaveBeenCalledTimes(3)
//       expect(retry).toHaveBeenCalledTimes(2)
//       expect(onSuccess).toHaveBeenCalledTimes(1)
//       expect(onError).toHaveBeenCalledTimes(0)
//     })

//     it('keeps polling during backend outage', async () => {
//       const store = mockStore()

//       const test = jest.fn(() => true)
//       const retry = jest.fn()
//       const onSuccess = jest.fn()
//       const onError = jest.fn()

//       mockAxios.get.mockRejectedValue({
//         message: 'Error',
//         response: {
//           status: 502,
//           data: { detail: 'Mock fail response' },
//         },
//       })

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
//       )

//       const actions = store.getActions()
//       expect(actions.length).toEqual(2)

//       expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[0].payload).toStrictEqual({
//         datafile_id: 1,
//         tryNumber: 1,
//         isPerformingRequest: true,
//         isDone: false,
//         error: null,
//       })

//       expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[1].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//         isDone: false,
//         error: {
//           message: 'Error',
//           response: {
//             status: 502,
//             data: { detail: 'Mock fail response' },
//           },
//         },
//       })

//       expect(test).toHaveBeenCalledTimes(0)
//       expect(retry).toHaveBeenCalledTimes(1)
//       expect(onSuccess).toHaveBeenCalledTimes(0)
//       expect(onError).toHaveBeenCalledTimes(0)
//     })

//     it('dispatches and calls onError when polling gets 400, 401, or 403', async () => {
//       const store = mockStore()

//       const test = jest.fn(() => true)
//       const retry = jest.fn()
//       const onSuccess = jest.fn()
//       const onError = jest.fn()

//       mockAxios.get.mockRejectedValue({
//         message: 'Error',
//         response: {
//           status: 403,
//           data: { detail: 'Mock fail response' },
//         },
//       })

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 1, test, retry, onSuccess, onError)
//       )

//       const actions = store.getActions()
//       expect(actions.length).toEqual(3)

//       expect(actions[0].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[0].payload).toStrictEqual({
//         datafile_id: 1,
//         tryNumber: 1,
//         isPerformingRequest: true,
//         isDone: false,
//         error: null,
//       })

//       expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[1].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//         isDone: true,
//         error: {
//           message: 'Error',
//           response: {
//             status: 403,
//             data: { detail: 'Mock fail response' },
//           },
//         },
//       })

//       expect(actions[2].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[2].payload).toStrictEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//         isDone: true,
//         error: new Error(
//           'The system encountered an error, please refresh the page or press Search again.'
//         ),
//       })

//       expect(test).toHaveBeenCalledTimes(0)
//       expect(retry).toHaveBeenCalledTimes(0)
//       expect(onSuccess).toHaveBeenCalledTimes(0)
//       expect(onError).toHaveBeenCalledTimes(1)
//     })

//     it('dispatches and calls onError when tryNumber > MAX_TRIES', async () => {
//       const store = mockStore()

//       const test = jest.fn(() => true)
//       const retry = jest.fn()
//       const onSuccess = jest.fn()
//       const onError = jest.fn()

//       mockAxios.get.mockResolvedValue({
//         data: { id: 1, hasErrors: true, summary: { status: 'Approved' } },
//       })

//       await store.dispatch(
//         pollFraSubmissionStatus(1, 31, test, retry, onSuccess, onError)
//       )

//       const actions = store.getActions()
//       expect(actions.length).toEqual(2)

//       expect(actions[0].type).toBe(SET_FRA_SUBMISSION_STATUS_TIMED_OUT)
//       expect(actions[0].payload).toEqual({
//         datafile_id: 1,
//       })

//       expect(actions[1].type).toBe(SET_IS_LOADING_FRA_SUBMISSION_STATUS)
//       expect(actions[1].payload).toEqual({
//         datafile_id: 1,
//         isPerformingRequest: false,
//         isDone: true,
//         error: new Error(
//           'The system encountered an error, please refresh the page or press Search again.'
//         ),
//       })

//       expect(test).toHaveBeenCalledTimes(0)
//       expect(retry).toHaveBeenCalledTimes(0)
//       expect(onSuccess).toHaveBeenCalledTimes(0)
//       expect(onError).toHaveBeenCalledTimes(1)
//     })
//   })
// })
