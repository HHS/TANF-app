import { render, fireEvent, waitFor, act } from '@testing-library/react'
import axios from 'axios'
import { usePollingTimer } from './usePollingTimer'

describe('usePollingTimer', () => {
  const setupMockFuncs = () => {
    jest.useFakeTimers()
    return {
      mockAxios: axios,
      requestFunc: jest.fn(() => {
        return axios.get('/fake_status_endpoint/')
      }),
      testFunc: jest.fn((response) => {
        return response?.data?.summary?.status !== 'Pending'
      }),
      onSuccessFunc: jest.fn((response) => response),
      onErrorFunc: jest.fn((error) => error),
      onTimeoutFunc: jest.fn((onError) => onError),
    }
  }

  const setupSingleTimerComponent = (mockFuncs, wait_time, max_tries) => {
    const requestId = 1
    const TestComponent = () => {
      const { startPolling, isPolling } = usePollingTimer()
      const onClickStart = () => {
        startPolling(
          requestId,
          mockFuncs.requestFunc,
          mockFuncs.testFunc,
          mockFuncs.onSuccessFunc,
          mockFuncs.onErrorFunc,
          mockFuncs.onTimeoutFunc,
          wait_time,
          max_tries
        )
      }

      const IsPollingText = ({ isLoading }) => (
        <p>{isLoading ? 'Polling' : 'Done'}</p>
      )

      return (
        <>
          <button onClick={onClickStart} title="Start" />
          <IsPollingText
            isLoading={
              isPolling && requestId in isPolling ? isPolling[requestId] : false
            }
          />
        </>
      )
    }

    return render(<TestComponent />)
  }

  const setupMultiTimerComponent = (mockFuncs, wait_time, max_tries) => {
    const TestComponent = () => {
      const { startPolling, isPolling } = usePollingTimer()
      const onClickStart = (requestId) =>
        startPolling(
          requestId,
          mockFuncs.requestFunc,
          mockFuncs.testFunc,
          mockFuncs.onSuccessFunc,
          mockFuncs.onErrorFunc,
          mockFuncs.onTimeoutFunc,
          wait_time,
          max_tries
        )

      const IsPollingText = ({ text, isLoading }) => (
        <p>{`${text} - ${isLoading ? 'Polling' : 'Done'}`}</p>
      )

      return (
        <>
          <button onClick={() => onClickStart(1)} title="Start 1" />
          <IsPollingText
            text="Timer 1"
            isLoading={isPolling && 1 in isPolling ? isPolling[1] : false}
          />

          <button onClick={() => onClickStart(2)} title="Start 2" />
          <IsPollingText
            text="Timer 2"
            isLoading={isPolling && 2 in isPolling ? isPolling[2] : false}
          />
        </>
      )
    }

    return render(<TestComponent />)
  }

  it('should not be polling when initialized', () => {
    const mocks = setupMockFuncs()
    const { getByText, queryByText } = setupSingleTimerComponent(
      mocks,
      1000,
      10
    )

    expect(getByText('Done')).toBeInTheDocument()
    expect(queryByText('Polling')).not.toBeInTheDocument()
  })

  it('should start polling when startPolling called', async () => {
    const mocks = setupMockFuncs()
    const { mockAxios } = mocks
    mockAxios.get.mockResolvedValue({
      data: { id: 1, hasErrors: false, summary: { status: 'Pending' } },
    })

    const { queryByText, getByTitle, getByText } = setupSingleTimerComponent(
      mocks,
      1000,
      10
    )

    expect(queryByText('Done')).toBeInTheDocument()
    expect(queryByText('Polling')).not.toBeInTheDocument()

    fireEvent.click(getByTitle('Start'))

    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Polling')).toBeInTheDocument()
      expect(queryByText('Done')).not.toBeInTheDocument()
    })
  })

  it('should call retry until the test completes then call onSuccess', async () => {
    const mocks = setupMockFuncs()
    const { mockAxios } = mocks
    mockAxios.get.mockResolvedValue({
      data: { id: 1, hasErrors: false, summary: { status: 'Pending' } },
    })

    const { queryByText, getByTitle, getByText } = setupSingleTimerComponent(
      mocks,
      1000,
      10
    )

    expect(queryByText('Done')).toBeInTheDocument()
    expect(queryByText('Polling')).not.toBeInTheDocument()

    fireEvent.click(getByTitle('Start'))

    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Polling')).toBeInTheDocument()
      expect(queryByText('Done')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(1)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    // run the timers again, but don't update the mock
    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Polling')).toBeInTheDocument()
      expect(queryByText('Done')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(2)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    // now update the mock and run a third time
    mockAxios.get.mockResolvedValue({
      data: { id: 1, hasErrors: false, summary: { status: 'Approved' } },
    })

    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Done')).toBeInTheDocument()
      expect(queryByText('Polling')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(3)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(1)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)
  })

  it.each([404, 500])(
    'should call retry when the backend is down',
    async (status) => {
      const mocks = setupMockFuncs()
      const { mockAxios } = mocks
      mockAxios.get.mockRejectedValue({
        message: 'Error',
        response: {
          status,
          data: { detail: 'Mock fail response' },
        },
      })

      const { queryByText, getByTitle, getByText } = setupSingleTimerComponent(
        mocks,
        1000,
        10
      )

      expect(queryByText('Done')).toBeInTheDocument()
      expect(queryByText('Polling')).not.toBeInTheDocument()

      fireEvent.click(getByTitle('Start'))

      act(() => jest.advanceTimersByTime(1000))

      await waitFor(() => {
        expect(queryByText('Polling')).toBeInTheDocument()
        expect(queryByText('Done')).not.toBeInTheDocument()
      })

      expect(mocks.requestFunc).toHaveBeenCalledTimes(1)
      expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
      expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
      expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

      // run the timers again, but don't update the mock
      act(() => jest.advanceTimersByTime(1000))

      await waitFor(() => {
        expect(queryByText('Polling')).toBeInTheDocument()
        expect(queryByText('Done')).not.toBeInTheDocument()
      })

      expect(mocks.requestFunc).toHaveBeenCalledTimes(2)
      expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
      expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
      expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)
    }
  )

  it.each([400, 401, 403])(
    'should stop polling and call onError if the request fails with a %s error',
    async (status) => {
      const mocks = setupMockFuncs()
      const { mockAxios } = mocks

      mockAxios.get.mockRejectedValue({
        message: 'Error',
        response: {
          status,
          data: { detail: 'Mock fail response' },
        },
      })

      const { queryByText, getByTitle, getByText } = setupSingleTimerComponent(
        mocks,
        1000,
        10
      )

      expect(queryByText('Done')).toBeInTheDocument()
      expect(queryByText('Polling')).not.toBeInTheDocument()

      fireEvent.click(getByTitle('Start'))

      act(() => jest.advanceTimersByTime(1000))

      await waitFor(() => {
        expect(queryByText('Done')).toBeInTheDocument()
        expect(queryByText('Polling')).not.toBeInTheDocument()
      })

      expect(mocks.requestFunc).toHaveBeenCalledTimes(1)
      expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
      expect(mocks.onErrorFunc).toHaveBeenCalledTimes(1)
      expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)
    }
  )

  it('should stop polling and call onTimeout when max tries reached', async () => {
    const mocks = setupMockFuncs()
    const { mockAxios } = mocks
    mockAxios.get.mockResolvedValue({
      data: { id: 1, hasErrors: false, summary: { status: 'Pending' } },
    })

    const { queryByText, getByTitle, getByText } = setupSingleTimerComponent(
      mocks,
      1000,
      2 // time out after 2 tries
    )

    expect(queryByText('Done')).toBeInTheDocument()
    expect(queryByText('Polling')).not.toBeInTheDocument()

    fireEvent.click(getByTitle('Start'))

    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Polling')).toBeInTheDocument()
      expect(queryByText('Done')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(1)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    // fire the timer again without updating the mocks
    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Polling')).toBeInTheDocument()
      expect(queryByText('Done')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(2)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)

    // because the timer calls `poll` again immediately, but doesn't fire the request
    // until `advanceTimersByTime` is called, the timeout is fired without
    // advancing the timers a third time
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(1)
  })

  // it('should prevent multiple parallel timers with the same requestId', async () => {
  //   const mocks = setupMockFuncs()
  //   const { mockAxios } = mocks
  //   mockAxios.get.mockResolvedValue({
  //     data: { id: 1, hasErrors: false, summary: { status: 'Pending' } },
  //   })

  //   const { queryByText, getByTitle, getByText } = setupSingleTimerComponent(
  //     mocks,
  //     1000,
  //     10
  //   )

  //   expect(queryByText('Done')).toBeInTheDocument()
  //   expect(queryByText('Polling')).not.toBeInTheDocument()

  //   fireEvent.click(getByTitle('Start'))

  //   await waitFor(() => {
  //     expect(queryByText('Polling')).toBeInTheDocument()
  //     expect(queryByText('Done')).not.toBeInTheDocument()
  //   })

  //   expect(mocks.requestFunc).toHaveBeenCalledTimes(1)
  //   expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
  //   expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
  //   expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

  //   // click start again, with the timer pending
  //   console.log('click start again')
  //   fireEvent.click(getByTitle('Start'))

  //   expect(mocks.requestFunc).toHaveBeenCalledTimes(1)
  //   expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
  //   expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
  //   expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)
  // })

  it('should allow multiple parallel timers with different requestIds', async () => {
    const mocks = setupMockFuncs()
    const { mockAxios } = mocks
    mockAxios.get.mockResolvedValue({
      data: { id: 1, hasErrors: false, summary: { status: 'Pending' } },
    })

    const { queryByText, getByTitle, getByText } = setupMultiTimerComponent(
      mocks,
      1000,
      10
    )

    expect(queryByText('Timer 1 - Done')).toBeInTheDocument()
    expect(queryByText('Timer 1 - Polling')).not.toBeInTheDocument()
    expect(queryByText('Timer 2 - Done')).toBeInTheDocument()
    expect(queryByText('Timer 2 - Polling')).not.toBeInTheDocument()

    fireEvent.click(getByTitle('Start 1'))

    act(() => jest.advanceTimersByTime(1000))

    await waitFor(() => {
      expect(queryByText('Timer 1 - Polling')).toBeInTheDocument()
      expect(queryByText('Timer 1 - Done')).not.toBeInTheDocument()
      expect(queryByText('Timer 2 - Done')).toBeInTheDocument()
      expect(queryByText('Timer 2 - Polling')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(1) // timer 1 starts
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    act(() => jest.advanceTimersByTime(1000))

    fireEvent.click(getByTitle('Start 2'))

    await waitFor(() => {
      expect(queryByText('Timer 1 - Polling')).toBeInTheDocument() // timer 1 retries, timer 2 starts
      expect(queryByText('Timer 1 - Done')).not.toBeInTheDocument()
      expect(queryByText('Timer 2 - Polling')).toBeInTheDocument()
      expect(queryByText('Timer 2 - Done')).not.toBeInTheDocument()
    })

    expect(mocks.requestFunc).toHaveBeenCalledTimes(3)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    await waitFor(() => {
      expect(queryByText('Timer 1 - Polling')).toBeInTheDocument()
      expect(queryByText('Timer 1 - Done')).not.toBeInTheDocument()
      expect(queryByText('Timer 2 - Polling')).toBeInTheDocument()
      expect(queryByText('Timer 2 - Done')).not.toBeInTheDocument()
    })

    act(() => jest.advanceTimersByTime(1000))

    expect(mocks.requestFunc).toHaveBeenCalledTimes(5) // both timers retry
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    await waitFor(() => {
      expect(queryByText('Timer 1 - Polling')).toBeInTheDocument()
      expect(queryByText('Timer 1 - Done')).not.toBeInTheDocument()
      expect(queryByText('Timer 2 - Polling')).toBeInTheDocument()
      expect(queryByText('Timer 2 - Done')).not.toBeInTheDocument()
    })
  })

  it('should clear all timers when un-mounted', async () => {
    jest.spyOn(global, 'setTimeout')
    jest.spyOn(global, 'clearTimeout')
    const mocks = setupMockFuncs()
    const { mockAxios } = mocks
    mockAxios.get.mockResolvedValue({
      data: { id: 1, hasErrors: false, summary: { status: 'Pending' } },
    })

    const { queryByText, getByTitle, unmount } = setupMultiTimerComponent(
      mocks,
      1000,
      10
    )

    expect(queryByText('Timer 1 - Done')).toBeInTheDocument()
    expect(queryByText('Timer 1 - Polling')).not.toBeInTheDocument()
    expect(queryByText('Timer 2 - Done')).toBeInTheDocument()
    expect(queryByText('Timer 2 - Polling')).not.toBeInTheDocument()

    fireEvent.click(getByTitle('Start 1'))
    fireEvent.click(getByTitle('Start 2'))

    act(() => jest.advanceTimersByTime(1000))

    expect(mocks.requestFunc).toHaveBeenCalledTimes(2)
    expect(mocks.onSuccessFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onErrorFunc).toHaveBeenCalledTimes(0)
    expect(mocks.onTimeoutFunc).toHaveBeenCalledTimes(0)

    expect(setTimeout).toHaveBeenCalledTimes(2)

    act(() => jest.advanceTimersByTime(1000))

    unmount()

    expect(clearTimeout).toHaveBeenCalledTimes(2)
  })
})
