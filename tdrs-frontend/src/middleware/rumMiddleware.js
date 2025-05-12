import { logUserAction } from '../services/RumService'

/**
 * Redux middleware for tracking Redux actions and state changes
 * This middleware logs all Redux actions as user actions for RUM analytics
 * @param {Object} store - Redux store
 * @returns {Function} - Redux middleware function
 */
const rumMiddleware = (store) => (next) => (action) => {
  // Skip certain high-frequency actions to reduce noise
  const skipActions = ['@@router', 'IDLE_TIMER']
  const shouldSkip = skipActions.some((prefix) =>
    action.type.startsWith(prefix)
  )

  if (!shouldSkip) {
    const startTime = performance.now()
    const result = next(action)
    const duration = performance.now() - startTime

    // Log the action with its duration
    logUserAction('redux_action', {
      type: action.type,
      duration: Math.round(duration),
      // Include a safe subset of the action payload
      // Avoid logging sensitive data or large objects
      hasPayload: !!action.payload,
    })

    return result
  }

  return next(action)
}

export default rumMiddleware
