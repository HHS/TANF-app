/**
 * Mocks fetch-instance HTTP requests.
 */

export const get = jest.fn(() =>
  Promise.resolve({
    data: {},
    error: null,
    status: 200,
    ok: true,
  })
)

export const post = jest.fn(() =>
  Promise.resolve({
    data: {},
    error: null,
    status: 200,
    ok: true,
  })
)

export const patch = jest.fn(() =>
  Promise.resolve({
    data: {},
    error: null,
    status: 200,
    ok: true,
  })
)

export default { get, post, patch }
