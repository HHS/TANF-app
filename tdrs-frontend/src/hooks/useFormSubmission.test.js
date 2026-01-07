import { render, screen, act } from '@testing-library/react'
import { useFormSubmission } from './useFormSubmission'

// Helper component to test the hook
function TestComponent({ testFn }) {
  const hookResult = useFormSubmission()
  testFn(hookResult)
  return (
    <div data-testid="isSubmitting">{hookResult.isSubmitting.toString()}</div>
  )
}

describe('useFormSubmission', () => {
  it('should initialize with isSubmitting as false', () => {
    let hookResult
    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )
    expect(hookResult.isSubmitting).toBe(false)
    expect(screen.getByTestId('isSubmitting').textContent).toBe('false')
  })

  it('should set isSubmitting to true when onSubmitStart is called', () => {
    let hookResult
    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    act(() => {
      hookResult.onSubmitStart()
    })

    expect(hookResult.isSubmitting).toBe(true)
    expect(screen.getByTestId('isSubmitting').textContent).toBe('true')
  })

  it('should set isSubmitting to false when onSubmitComplete is called', () => {
    let hookResult
    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    // First set it to true
    act(() => {
      hookResult.onSubmitStart()
    })

    // Then set it back to false
    act(() => {
      hookResult.onSubmitComplete()
    })

    expect(hookResult.isSubmitting).toBe(false)
    expect(screen.getByTestId('isSubmitting').textContent).toBe('false')
  })

  it('should execute the submission function and return its result', async () => {
    let hookResult
    const mockSubmitFn = jest.fn().mockResolvedValue('success')

    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    let returnValue
    await act(async () => {
      returnValue = await hookResult.executeSubmission(mockSubmitFn)
    })

    expect(mockSubmitFn).toHaveBeenCalledTimes(1)
    expect(returnValue).toBe('success')
    expect(hookResult.isSubmitting).toBe(false)
    expect(screen.getByTestId('isSubmitting').textContent).toBe('false')
  })

  it('should call onSuccess callback when submission succeeds', async () => {
    let hookResult
    const mockSubmitFn = jest.fn().mockResolvedValue('success')
    const onSuccess = jest.fn()

    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    await act(async () => {
      await hookResult.executeSubmission(mockSubmitFn, { onSuccess })
    })

    expect(onSuccess).toHaveBeenCalledWith('success')
    expect(hookResult.isSubmitting).toBe(false)
  })

  it('should call onError callback when submission fails', async () => {
    let hookResult
    const error = new Error('Submission failed')
    const mockSubmitFn = jest.fn().mockRejectedValue(error)
    const onError = jest.fn()

    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    let promise
    await act(async () => {
      promise = hookResult.executeSubmission(mockSubmitFn, { onError })
      // Need to catch the error to prevent test failure
      try {
        await promise
      } catch (e) {
        // Expected error
      }
    })

    expect(onError).toHaveBeenCalledWith(error)
    expect(hookResult.isSubmitting).toBe(false)
  })

  it('should re-throw error when submission fails without onError callback', async () => {
    let hookResult
    const mockSubmitFn = jest.fn(() => {
      throw new Error('Submission failed without callback')
    })

    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    let promise
    await act(async () => {
      promise = hookResult.executeSubmission(mockSubmitFn)
      try {
        await promise
      } catch (e) {
        expect(e.message).toEqual('Submission failed without callback')
      }
    })
    expect(hookResult.isSubmitting).toBe(false)
  })

  it('should prevent multiple submissions when isSubmitting is true', async () => {
    let hookResult
    const mockSubmitFn = jest.fn().mockResolvedValue('success')

    render(
      <TestComponent
        testFn={(result) => {
          hookResult = result
        }}
      />
    )

    // Manually set isSubmitting to true
    act(() => {
      hookResult.onSubmitStart()
    })

    // Try to execute submission while already submitting
    act(() => {
      hookResult.executeSubmission(mockSubmitFn)
    })

    // The submit function should not be called
    expect(mockSubmitFn).not.toHaveBeenCalled()
  })
})
