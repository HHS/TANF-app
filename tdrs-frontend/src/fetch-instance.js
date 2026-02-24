import { faro } from '@grafana/faro-react'

function getCSRFToken() {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]*)/)
  return match ? decodeURIComponent(match[1]) : null
}

function buildHeaders(customHeaders = {}, includeCSRF = true) {
  const headers = { 'x-service-name': 'tdp-frontend', ...customHeaders }

  if (includeCSRF) {
    const csrfToken = getCSRFToken()
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }

  if (faro?.api) {
    try {
      const traceContext = faro.api.getTraceContext()
      if (traceContext) Object.assign(headers, traceContext)
    } catch (e) {
      console.error('Failed to add trace context', e)
    }
  }

  return headers
}

async function handleResponse(response, responseType) {
  if (responseType === 'blob') {
    return {
      data: await response.blob(),
      error: response.ok ? null : new Error(`HTTP ${response.status}`),
      status: response.status,
      ok: response.ok,
    }
  }

  const contentType = response.headers.get('content-type') || ''
  let data = null

  if (contentType.includes('application/json')) {
    data = await response.json().catch(() => null)
  } else {
    data = await response.text()
  }

  return {
    data,
    error: response.ok ? null : new Error(`HTTP ${response.status}`),
    status: response.status,
    ok: response.ok,
  }
}

export async function get(url, options = {}) {
  const { headers: customHeaders, responseType, params, ...rest } = options

  let finalUrl = url
  if (params) {
    const searchParams = new URLSearchParams(params)
    finalUrl = `${url}?${searchParams.toString()}`
  }

  try {
    const response = await fetch(finalUrl, {
      method: 'GET',
      credentials: 'include',
      headers: buildHeaders(customHeaders, false),
      ...rest,
    })
    return handleResponse(response, responseType)
  } catch (error) {
    return { data: null, error, status: 0, ok: false }
  }
}

export async function post(url, body, options = {}) {
  const { headers: customHeaders, ...rest } = options
  const isFormData = body instanceof FormData
  const headers = buildHeaders(
    isFormData
      ? customHeaders
      : { 'Content-Type': 'application/json', ...customHeaders },
    true
  )

  if (isFormData) {
    delete headers['Content-Type']
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers,
      body: isFormData ? body : JSON.stringify(body),
      ...rest,
    })
    return handleResponse(response)
  } catch (error) {
    return { data: null, error, status: 0, ok: false }
  }
}

export async function patch(url, body, options = {}) {
  const { headers: customHeaders, ...rest } = options

  try {
    const response = await fetch(url, {
      method: 'PATCH',
      credentials: 'include',
      headers: buildHeaders(
        { 'Content-Type': 'application/json', ...customHeaders },
        true
      ),
      body: JSON.stringify(body),
      ...rest,
    })
    return handleResponse(response)
  } catch (error) {
    return { data: null, error, status: 0, ok: false }
  }
}

export default { get, post, patch }
