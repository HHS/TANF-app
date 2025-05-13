import { initializeFaro } from '@grafana/faro-web-sdk'
import { TracingInstrumentation } from '@grafana/faro-web-tracing'
import {
  ReactIntegration,
  getWebInstrumentations,
  createReactRouterV6Options,
} from '@grafana/faro-react'
import {
  createRoutesFromChildren,
  matchRoutes,
  Routes,
  useLocation,
  useNavigationType,
} from 'react-router-dom'

/**
 * Initialize and configure the Grafana Faro RUM SDK
 * This service tracks user sessions, page performance metrics, and application events
 * for integration with Grafana dashboards.
 */
const initializeRum = () => {
  // Only initialize in production or if explicitly enabled in other environments
  if (
    process.env.NODE_ENV !== 'production' &&
    !process.env.REACT_APP_ENABLE_RUM
  ) {
    console.log(
      'RUM disabled in development. Set REACT_APP_ENABLE_RUM=true to enable.'
    )
    return null
  }

  try {
    const faro = initializeFaro({
      url: process.env.REACT_APP_FARO_ENDPOINT,
      app: {
        name: 'tdp-frontend',
        version: process.env.REACT_APP_VERSION,
        environment: process.env.NODE_ENV,
      },
      // Set a reasonable sample rate to control data volume
      sessionSampleRate: 0.5,
      instrumentations: [
        // Load the default Web instrumentations
        ...getWebInstrumentations({ captureConsole: true }),
        // Trace API calls and other async operations
        new TracingInstrumentation(),
        // Add React-specific instrumentation
        new ReactIntegration({
          // Track components that take >50ms to render
          componentRenderThreshold: 50,
          router: createReactRouterV6Options({
            createRoutesFromChildren,
            matchRoutes,
            Routes,
            useLocation,
            useNavigationType,
          }),
        }),
      ],
      meta: {
        // Add any application-specific metadata here
        appType: 'TANF Data Portal',
      },
    })

    console.log('Grafana Faro RUM initialized successfully')
    return faro
  } catch (error) {
    // Fail gracefully - RUM should never break the application
    console.error('Failed to initialize RUM:', error)
    return null
  }
}

// Export a singleton instance
const faroInstance = initializeRum()

export default faroInstance

export const setUserInfo = (user) => {
  if (!faroInstance || !faroInstance.api) return

  // Set user information in Faro
  faroInstance.api.setUser({
    email: user.email,
    id: user.id,
    username: user.username,
    attributes: {
      role: user.roles,
      // Add service name directly in user attributes to ensure proper attribution
      serviceName: 'tdp-frontend',
    },
  })

  if (faroInstance.api.pushMeta) {
    faroInstance.api.pushMeta({
      'enduser.id': user.id,
      'enduser.username': user.username,
      'enduser.role': user.roles,
      'service.name': 'tdp-frontend',
    })
  }
}

/**
 * Create a traced span for a user action
 * @param {string} actionName - Name of the action being performed
 * @param {Function} callback - Function to execute within the span
 * @returns {*} - Result of the callback function
 */
export const traceUserAction = (actionName, callback) => {
  if (!faroInstance || !faroInstance.api) {
    return callback()
  }

  // Check if tracing is available in this version of Faro
  if (!faroInstance.api.getTracer) {
    // Fallback to just logging the action if tracing isn't available
    console.log(`Tracing action: ${actionName}`)
    return callback()
  }

  try {
    const tracer = faroInstance.api.getTracer('user-actions')
    return tracer.startActiveSpan(`User Action: ${actionName}`, (span) => {
      // Add attributes to the span
      if (span.setAttribute) {
        span.setAttribute('service.name', 'tdp-frontend')
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
  if (!faroInstance) return

  faroInstance.api.pushEvent('page_view', {
    page: pageName,
    timestamp: Date.now(),
    service_name: 'tdp-frontend',
  })
}

export const logUserAction = (actionName, details = {}) => {
  if (!faroInstance) return

  faroInstance.api.pushEvent('user_action', {
    action: actionName,
    ...details,
    timestamp: Date.now(),
    service_name: 'tdp-frontend',
  })
}

export const logError = (error, context = {}) => {
  if (!faroInstance) return

  faroInstance.api.pushError(error, {
    ...context,
    timestamp: Date.now(),
    service_name: 'tdp-frontend',
  })
}
