import { useEffect, useRef, useState } from 'react'

const WAIT_TIME = 2000
const MAX_TRIES = 30

export const usePollingTimer = () => {
  const timers = useRef({})
  const [pollState, setPollState] = useState({})

  const setPollStateForRequest = (requestId, changes = {}) => {
    let newState = pollState
    newState[requestId] = {
      ...pollState[requestId],
      ...changes,
    }
    setPollState(newState)
  }

  const addTimer = (requestId, timer) => {
    timers.current[requestId] = timer
  }

  const getTimer = (requestId) => {
    if (timers.current && timers.current[requestId]) {
      return timers.current[requestId]
    }
    return null
  }

  const stopTimer = (requestId, deleteRef = true) => {
    clearTimeout(timers.current[requestId])

    if (deleteRef) {
      delete timers.current[requestId]
    }
  }

  const reset = (requestId) => {
    setPollStateForRequest(requestId, {
      isDonePolling: false,
      isPerformingRequest: false,
    })
  }

  const start = (requestId) => {
    setPollStateForRequest(requestId, { isPerformingRequest: true })
  }

  const finish = (requestId, then = () => null) => {
    setPollStateForRequest(requestId, {
      isDonePolling: true,
      isPerformingRequest: false,
    })
    stopTimer(requestId)
    then()
  }

  const poll = async (
    requestId,
    tryNumber = 1,
    request = () => null,
    test = (response) => null,
    onSuccess = (response) => null,
    onError = (error) => null,
    onTimeout = (onError) => null,
    wait_time = WAIT_TIME,
    max_tries = MAX_TRIES
  ) => {
    if (tryNumber > max_tries) {
      finish(requestId, () => onTimeout(onError))
      return
    }

    const timer = getTimer(requestId)
    if (timer && (timer.isPerformingRequest || timer.isDonePolling)) {
      finish(requestId, () =>
        onError({ message: 'Already performing request.' })
      )
      return
    }

    const retry = () => {
      setPollStateForRequest(requestId, { isPerformingRequest: false })
      poll(
        requestId,
        tryNumber + 1,
        request,
        test,
        onSuccess,
        onError,
        onTimeout,
        wait_time,
        max_tries
      )
    }

    const fetchAndTest = async () => {
      let response = null

      start(requestId)

      try {
        response = await request()
      } catch (axiosError) {
        const statusCode = axiosError?.response?.status
        const shouldStopPolling =
          statusCode === 400 || statusCode === 401 || statusCode === 403

        if (!shouldStopPolling) {
          retry(requestId, tryNumber)
          return
        }

        finish(requestId, () => onError(axiosError))
        return
      }

      let result = test(response)

      if (result) {
        finish(requestId, () => onSuccess(response))
        return
      } else {
        retry()
        return
      }
    }

    let timeout = setTimeout(fetchAndTest, tryNumber === 1 ? 0 : wait_time)
    addTimer(requestId, timeout)
  }

  const startPolling = (
    requestId,
    request = () => null,
    test = (response) => null,
    onSuccess = (response) => null,
    onError = (error, retry) => null,
    onTimeout = (onError) => null,
    wait_time = WAIT_TIME,
    max_tries = MAX_TRIES
  ) => {
    reset(requestId)
    poll(
      requestId,
      1,
      request,
      test,
      onSuccess,
      onError,
      onTimeout,
      wait_time,
      max_tries
    )
  }

  const isDonePolling = (requestId = null) => {
    if (requestId) {
      return timers.current && timers.current[requestId]
        ? timers.current[requestId].isDonePolling
        : true
    } else if (timers.current) {
      return Object.keys(timers.current)
        .map((t) => t.isDonePolling)
        .some((isDone) => isDone)
    }
    return true
  }

  useEffect(() => {
    const stopAllTimers = () => {
      Object.keys(timers.current).forEach((requestId) =>
        stopTimer(requestId, false)
      )
    }

    const timer = timers.current
    if (timer && Object.keys(timer).length === 0) {
      stopAllTimers()
    }
  }, [timers])

  return { startPolling, isDonePolling }
}
