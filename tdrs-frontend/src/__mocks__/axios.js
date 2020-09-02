/**
 * Mocks axios GET requests.
 */
export default {
  get: jest.fn(() =>
    Promise.resolve({
      data: {},
    })
  ),
}
