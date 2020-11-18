/**
 * Mocks axios GET requests.
 */

const mockAxios = jest.genMockFromModule('axios')
mockAxios.create = jest.fn(() => mockAxios)
mockAxios.get = jest.fn(() =>
  Promise.resolve({
    data: {},
  })
)

export default mockAxios
