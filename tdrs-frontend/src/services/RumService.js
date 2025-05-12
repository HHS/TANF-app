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
        name: 'TDP Frontend',
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
      // Collect browser and device metadata
      meta: {
        // Add any application-specific metadata here
        appType: 'TANF Data Portal',
      },
    })

    // Add custom attributes that will be attached to all events
    // faro.api.pushMeta({
    //   userType: localStorage.getItem('userRole') || 'unknown',
    // })

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

// Helper functions for manual instrumentation
export const logPageView = (pageName) => {
  if (!faroInstance) return

  faroInstance.api.pushEvent('page_view', {
    page: pageName,
    timestamp: Date.now(),
  })
}

export const logUserAction = (actionName, details = {}) => {
  if (!faroInstance) return

  faroInstance.api.pushEvent('user_action', {
    action: actionName,
    ...details,
    timestamp: Date.now(),
  })
}

export const logError = (error, context = {}) => {
  if (!faroInstance) return

  faroInstance.api.pushError(error, {
    ...context,
    timestamp: Date.now(),
  })
}
