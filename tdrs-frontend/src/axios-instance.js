import axios from 'axios'
import { faro } from '@grafana/faro-react'

// Need a custom instance of axios so we can set the csrf keys on auth_check
// Work around for csrf cookie issue we encountered in production.
// It may still be possible to do this with a cookie, and something on the
// frontend (most likely) is misconfigured. the configuration has alluded
// us thus far, and this implementation is functionally equivalent to
// using cookies.

const axiosInstance = axios.create()

// Add an interceptor to include trace context in outgoing requests for custom instance and default instance
axios.interceptors.request.use((config) => {
  try {
    // Add service name to the request
    config.headers = config.headers || {}
    config.headers['x-service-name'] = 'tdp-frontend'
    // Add trace context if Faro is initialized
    if (faro && faro.api) {
      const traceContext = faro.api.getTraceContext()
      if (traceContext) {
        // Add W3C trace context headers
        Object.assign(config.headers, traceContext)
      }
    }
  } catch (e) {
    console.error('Failed to add trace context', e)
  }
  return config
})

axiosInstance.interceptors.request.use((config) => {
  try {
    // Add service name to the request
    config.headers = config.headers || {}
    config.headers['x-service-name'] = 'tdp-frontend'
    // Add trace context if Faro is initialized
    if (faro && faro.api) {
      const traceContext = faro.api.getTraceContext()
      if (traceContext) {
        // Add W3C trace context headers
        Object.assign(config.headers, traceContext)
      }
    }
  } catch (e) {
    console.error('Failed to add trace context', e)
  }
  return config
})

export default axiosInstance
