import { createServer } from 'miragejs'
import { v4 as uuidv4 } from 'uuid'

export default function startMirage(
  { environment } = { environment: 'development' }
) {
  return createServer({
    environment,

    routes() {
      this.namespace = 'mock_api'

      // Allow unhandled requests to pass through
      this.passthrough(`${process.env.REACT_APP_BACKEND_URL}/**`)
      this.passthrough(`${process.env.REACT_APP_BACKEND_HOST}/**`)
    },
  })
}
