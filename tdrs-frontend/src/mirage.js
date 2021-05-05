import { createServer } from 'miragejs'
import { v4 as uuidv4 } from 'uuid'

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
      this.get('/reports/:year/:quarter/', () => {
        return [
          {
            fileName: 'test.txt',
            section: '1 - Active Case Data',
            uuid: uuidv4(),
          },
          {
            fileName: 'testb.txt',
            section: '2 - Closed Case Data',
            uuid: uuidv4(),
          },
        ]
      })

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)
    },
  })
}
