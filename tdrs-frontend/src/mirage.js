import { createServer, Response } from 'miragejs'
import {
  AUTH_CHECK_DATA,
  FAILED_AUTH_CHECK_DATA,
  STT_ALPHA_DATA,
  REPORTS_DATA,
} from './mirage.data.js'

export default function startMirage(
  { environment } = { environment: 'development' }
) {
  return createServer({
    environment,

    routes() {
      if (process.env.REACT_APP_MOCK_API || process.env.REACT_APP_PA11Y_TEST) {
        this.urlPrefix = 'http://localhost:8080/v1'
        this.post('/reports/', () => 'Success')
        this.get('/auth_check/', () => {
          if (
            window.localStorage.getItem('loggedIn') ||
            process.env.REACT_APP_PA11Y_TEST
          ) {
            return AUTH_CHECK_DATA
          } else {
            return FAILED_AUTH_CHECK_DATA
          }
        })
        this.patch('/users/set_profile', () => {
          return {}
        })
        this.get('/stts/alpha', () => STT_ALPHA_DATA)
        this.get('/reports/', () => REPORTS_DATA)
      }

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)

      console.log('Done Building routes')
    },
  })
}
