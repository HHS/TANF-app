import { createServer } from 'miragejs'

export default function startMirage(
  { environment } = { environment: 'development' }
) {
  return createServer({
    environment,

    routes() {
      this.namespace = 'mock_api'

      this.post('/reports/signed_url/', () => {
        return {
          signed_url: '/mock_api/signed_s3_url/',
        }
      })

      this.put('/signed_s3_url/', () => {
        return 'Success'
      })

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)
    },
  })
}
