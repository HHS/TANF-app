import { faro } from '@grafana/faro-react'

export const setUserInfo = (user) => {
  // if (!faro || !faro.api) return
  console.log('Setting user to:', JSON.stringify(user, null, 2))

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
 * Create a traced span for a user action
 * @param {string} actionName - Name of the action being performed
 * @param {Function} callback - Function to execute within the span
 * @returns {*} - Result of the callback function
 */
export const traceUserAction = (actionName, callback) => {
  if (!faro || !faro.api) {
    return callback()
  }

  // Check if tracing is available in this version of Faro
  if (!faro.api.getTracer) {
    // Fallback to just logging the action if tracing isn't available
    console.log(`Tracing action: ${actionName}`)
    return callback()
  }

  try {
    const tracer = faro.api.getTracer('user-actions')
    return tracer.startActiveSpan(`User Action: ${actionName}`, (span) => {
      // Add attributes to the span
      if (span.setAttribute) {
        span.setAttribute('action.name', actionName)
      }

      try {
        const result = callback()
        span.end()
        return result
      } catch (error) {
        if (span.recordException) {
          span.recordException(error)
        }
        if (span.setStatus) {
          span.setStatus({ code: 2, message: error.message }) // Error status
        }
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
export const logPageView = (pageName) => {
  if (!faro) return

  // Structure data in a way that Alloy can process
  // Using event_data_ prefix for fields that should be extracted
  const eventData = {
    page: pageName,
    timestamp: Date.now(),
  }

  console.log('Sending page_view event with data:', eventData)
  faro.api.pushEvent('page_view', eventData)
}

export const logUserAction = (actionName, details = {}) => {
  if (!faro) return

  faro.api.pushEvent('user_action', {
    action: actionName,
    ...details,
    timestamp: Date.now(),
  })
}

export const logError = (error, context = {}) => {
  if (!faro) return

  faro.api.pushError(error, {
    ...context,
    timestamp: Date.now(),
  })
}
