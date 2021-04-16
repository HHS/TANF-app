import { createServer } from 'miragejs'

export default function startMirage(
  { environment } = { environment: 'development' }
) {
  return createServer({
    environment,

    routes() {
      this.namespace = 'mock_api'

      this.post('/reports/', () => {
        return 'Success'
      })
      this.get('/reports/data-files/:year/:quarter/:section', () => {
        return 'some text'
      })

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)
    },
  })
}
