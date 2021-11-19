import { createServer } from 'miragejs'
import { v4 as uuidv4 } from 'uuid'
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
      this.urlPrefix = 'http://localhost:8080/v1'
      this.get('/auth_check', () => {
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
      this.post('/logs/', () => {})
      this.post('/reports/', () => 'Success')

      // if/when we add cypress tests, the rest of these
      // routes will need some work done on them

      this.patch('/users/set_profile', () => {
        return {}
      })
      this.get('/stts/alpha', () => STT_ALPHA_DATA)
      this.get('/reports/', () => REPORTS_DATA)
      this.get('/reports/data-files/:year/:quarter/:section', () => {
        return 'some text'
      })
      this.get('/reports/:year/:quarter/', () => {
        return [
          {
            fileName: 'test.txt',
            section: 'Active Case Data',
            uuid: uuidv4(),
          },
          {
            fileName: 'testb.txt',
            section: 'Closed Case Data',
            uuid: uuidv4(),
          },
        ]
      })

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)

      console.log('Done Building routes')
    },
  })
}
