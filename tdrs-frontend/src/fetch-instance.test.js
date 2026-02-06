import { get, post, patch, setCSRFToken, getCSRFToken } from './fetch-instance'
import { faro } from '@grafana/faro-react'

jest.mock('@grafana/faro-react')

const mockResponse = (body, options = {}) => ({
  ok: options.ok !== undefined ? options.ok : true,
  status: options.status || 200,
  headers: {
    get: (key) => options.contentType || 'application/json',
  },
  json: () => Promise.resolve(body),
  text: () => Promise.resolve(typeof body === 'string' ? body : JSON.stringify(body)),
  blob: () => Promise.resolve(new Blob([JSON.stringify(body)])),
})

describe('fetch-instance', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    global.fetch = jest.fn()
    setCSRFToken(null)
  })

  describe('setCSRFToken / getCSRFToken', () => {
    it('stores and retrieves the CSRF token', () => {
      expect(getCSRFToken()).toBeNull()
      setCSRFToken('test-token')
      expect(getCSRFToken()).toBe('test-token')
    })
  })

  describe('get', () => {
    it('makes a GET request and returns JSON data', async () => {
      const data = { message: 'hello' }
      global.fetch.mockResolvedValue(mockResponse(data))

      const result = await get('/api/test')

      expect(fetch).toHaveBeenCalledWith('/api/test', {
        method: 'GET',
        credentials: 'include',
        headers: expect.objectContaining({
          'x-service-name': 'tdp-frontend',
        }),
      })
      expect(result).toEqual({ data, error: null, status: 200, ok: true })
    })

    it('returns error info for non-ok responses', async () => {
      global.fetch.mockResolvedValue(
        mockResponse({ detail: 'Not found' }, { ok: false, status: 404 })
      )

      const result = await get('/api/missing')

      expect(result.ok).toBe(false)
      expect(result.status).toBe(404)
      expect(result.error).toBeInstanceOf(Error)
      expect(result.error.message).toBe('HTTP 404')
    })

    it('handles network errors', async () => {
      const networkError = new Error('Network failure')
      global.fetch.mockRejectedValue(networkError)

      const result = await get('/api/down')

      expect(result).toEqual({
        data: null,
        error: networkError,
        status: 0,
        ok: false,
      })
    })

    it('handles blob response type', async () => {
      const blob = new Blob(['file-data'])
      global.fetch.mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => 'application/octet-stream' },
        blob: () => Promise.resolve(blob),
      })

      const result = await get('/api/download', { responseType: 'blob' })

      expect(result.data).toBe(blob)
      expect(result.ok).toBe(true)
      expect(result.error).toBeNull()
    })

    it('handles non-JSON text responses', async () => {
      global.fetch.mockResolvedValue(
        mockResponse('plain text', { contentType: 'text/plain' })
      )

      const result = await get('/api/text')

      expect(result.data).toBe('plain text')
      expect(result.ok).toBe(true)
    })
  })

  describe('post', () => {
    it('makes a POST request with JSON body', async () => {
      const responseData = { id: 1 }
      global.fetch.mockResolvedValue(mockResponse(responseData))

      const result = await post('/api/create', { name: 'test' })

      expect(fetch).toHaveBeenCalledWith('/api/create', {
        method: 'POST',
        credentials: 'include',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'x-service-name': 'tdp-frontend',
        }),
        body: JSON.stringify({ name: 'test' }),
      })
      expect(result).toEqual({ data: responseData, error: null, status: 200, ok: true })
    })

    it('makes a POST request with FormData', async () => {
      global.fetch.mockResolvedValue(mockResponse({ id: 2 }))
      const formData = new FormData()
      formData.append('file', 'test-file')

      await post('/api/upload', formData)

      const callArgs = fetch.mock.calls[0][1]
      expect(callArgs.body).toBe(formData)
      expect(callArgs.headers['Content-Type']).toBeUndefined()
    })

    it('includes CSRF token in POST headers', async () => {
      setCSRFToken('my-csrf-token')
      global.fetch.mockResolvedValue(mockResponse({}))

      await post('/api/create', {})

      expect(fetch).toHaveBeenCalledWith('/api/create', expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRFToken': 'my-csrf-token',
        }),
      }))
    })

    it('handles network errors', async () => {
      const networkError = new Error('Connection refused')
      global.fetch.mockRejectedValue(networkError)

      const result = await post('/api/create', {})

      expect(result).toEqual({
        data: null,
        error: networkError,
        status: 0,
        ok: false,
      })
    })
  })

  describe('patch', () => {
    it('makes a PATCH request with JSON body', async () => {
      const responseData = { updated: true }
      global.fetch.mockResolvedValue(mockResponse(responseData))

      const result = await patch('/api/update/1', { name: 'updated' })

      expect(fetch).toHaveBeenCalledWith('/api/update/1', {
        method: 'PATCH',
        credentials: 'include',
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          'x-service-name': 'tdp-frontend',
        }),
        body: JSON.stringify({ name: 'updated' }),
      })
      expect(result).toEqual({ data: responseData, error: null, status: 200, ok: true })
    })

    it('includes CSRF token in PATCH headers', async () => {
      setCSRFToken('patch-csrf-token')
      global.fetch.mockResolvedValue(mockResponse({}))

      await patch('/api/update/1', {})

      expect(fetch).toHaveBeenCalledWith('/api/update/1', expect.objectContaining({
        headers: expect.objectContaining({
          'X-CSRFToken': 'patch-csrf-token',
        }),
      }))
    })

    it('handles network errors', async () => {
      const networkError = new Error('Timeout')
      global.fetch.mockRejectedValue(networkError)

      const result = await patch('/api/update/1', {})

      expect(result).toEqual({
        data: null,
        error: networkError,
        status: 0,
        ok: false,
      })
    })
  })

  describe('faro trace context', () => {
    it('includes trace context headers when faro is available', async () => {
      faro.api.getTraceContext.mockReturnValue({ traceparent: 'test-trace-id' })
      global.fetch.mockResolvedValue(mockResponse({}))

      await get('/api/test')

      expect(faro.api.getTraceContext).toHaveBeenCalled()
      expect(fetch).toHaveBeenCalledWith('/api/test', expect.objectContaining({
        headers: expect.objectContaining({
          traceparent: 'test-trace-id',
        }),
      }))
    })

    it('handles faro getTraceContext throwing an error', async () => {
      faro.api.getTraceContext.mockImplementation(() => {
        throw new Error('faro error')
      })
      global.fetch.mockResolvedValue(mockResponse({}))
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation()

      await get('/api/test')

      expect(consoleSpy).toHaveBeenCalledWith(
        'Failed to add trace context',
        expect.any(Error)
      )
      expect(fetch).toHaveBeenCalled()
      consoleSpy.mockRestore()
    })
  })
})
