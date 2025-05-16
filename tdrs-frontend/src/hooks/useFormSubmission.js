import { useState } from 'react'

/**
 * Custom hook to manage form submission state and prevent multiple submissions
 * @returns {Object} Form submission utilities
 */
export const useFormSubmission = () => {
  const [isSubmitting, setIsSubmitting] = useState(false)

  /**
   * Execute a submission with proper state management
   * @param {Function} submitFn - The function to execute for submission
   * @param {Object} options - Additional options
   * @param {Function} options.onSuccess - Optional callback for success
   * @param {Function} options.onError - Optional callback for error
   * @returns {Promise} The result of the submission function
   */
  const executeSubmission = async (submitFn, options = {}) => {
    // Prevent multiple submissions
    if (isSubmitting) {
      return
    }

    // Set submitting state to true
    setIsSubmitting(true)

    try {
      // Execute the submission function
      const result = await submitFn()

      // Call success callback if provided
      if (options.onSuccess) {
        options.onSuccess(result)
      }
      return result
    } catch (error) {
      // Call error callback if provided
      if (options.onError) {
        options.onError(error)
      }
      // Re-throw the error for further handling
      throw error
    } finally {
      // Reset submitting state
      setIsSubmitting(false)
    }
  }

  return {
    isSubmitting,
    executeSubmission,
    onSubmitStart: () => setIsSubmitting(true),
    onSubmitComplete: () => setIsSubmitting(false),
  }
}
