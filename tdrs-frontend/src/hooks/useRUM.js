/* istanbul ignore file */
import { faro } from '@grafana/faro-react'

export const useRUM = () => {
  const setUserInfo = (user) => {
    if (!faro || !faro.api) {
      return
    }

    // Convert roles array to string to avoid unmarshal error
    const roleString = Array.isArray(user.roles)
      ? user.roles.map((role) => role.name).join(', ')
      : 'unknown'

    // Set user information in Faro
    faro.api.setUser({
      id: user.id,
      username: user.email,
      attributes: {
        role: roleString,
      },
    })
  }

  /**
   * Create a traced span for an async user action
   * @param {string} actionName - Name of the action being performed
   * @param {Function} callback - Async function to execute within the span
   * @returns {*} - Result of the callback function
   */
  const traceAsyncUserAction = async (actionName, callback) => {
    // Check if tracing is available
    if (!faro.api.getTracer || !faro) {
      return await callback()
    }

    try {
      const tracer = faro.api.getTracer('user-actions')
      return tracer.startActiveSpan(
        `User Action: ${actionName}`,
        async (span) => {
          try {
            span.setAttribute('action.name', actionName)
            const result = await callback()
            span.end()
            return result
          } catch (error) {
            span.recordException(error)
            span.setStatus({ code: 2, message: error.message })
            span.end()
            throw error
          }
        }
      )
    } catch (error) {
      // If anything fails in the tracing setup, still execute the callback
      console.error('Error in tracing:', error)
      return await callback()
    }
  }

  const traceUserAction = (actionName, callback) => {
    // Check if tracing is available
    if (!faro.api.getTracerm || !faro) {
      return callback()
    }

    try {
      const tracer = faro.api.getTracer('user-actions')
      return tracer.startActiveSpan(`User Action: ${actionName}`, (span) => {
        try {
          span.setAttribute('action.name', actionName)
          const result = callback()
          span.end()
          return result
        } catch (error) {
          span.recordException(error)
          span.setStatus({ code: 2, message: error.message })
          span.end()
          throw error
        }
      })
    } catch (error) {
      // If anything fails in the tracing setup, still execute the callback
      console.error('Error in tracing:', error)
      return callback()
    }
  }

  // Helper functions for manual instrumentation
  const logPageView = (pageName) => {
    if (!faro || !faro.api) {
      return
    }
    // Structure data in a way that Alloy can process
    // Using event_data_ prefix for fields that should be extracted
    const eventData = {
      page: pageName,
      timestamp: Date.now(),
    }

    faro.api.pushEvent('page_view', eventData)
  }

  const logUserAction = (actionName, details = {}) => {
    if (!faro || !faro.api) {
      return
    }
    faro.api.pushEvent('user_action', {
      action: actionName,
      ...details,
      timestamp: Date.now(),
    })
  }

  const logError = (error, context = {}) => {
    if (!faro || !faro.api) {
      return
    }
    faro.api.pushError(error, {
      ...context,
      timestamp: Date.now(),
    })
  }

  return {
    setUserInfo,
    traceAsyncUserAction,
    traceUserAction,
    logPageView,
    logUserAction,
    logError,
  }
}
