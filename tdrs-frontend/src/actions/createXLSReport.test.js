import { getParseErrors } from './createXLSReport'

it('should create an action to create an XLS report', () => {
  const data_json = {
    data: {},
    xls_report: 'aGVsbG8=',
  }
  // atob is not available in jest
  const expectedReturn = Error(
    'TypeError: URL.createObjectURL is not a function'
  )
  expect(getParseErrors(data_json)).toEqual(expectedReturn)
})

it('should create an action to create an XLS report and throwError', () => {
  const data_json = { data: {} }
  const expectedReturn = Error(
    'InvalidCharacterError: The string to be decoded contains invalid characters.'
  )
  expect(getParseErrors(data_json)).toEqual(expectedReturn)
})

it('should create an action to create an XLS report and throwError', () => {
  const documentIntial = { content: 'aaa' }
  global.URL.createObjectURL = jest.fn(() => 'myURL')
  global.Blob = jest.fn(() => documentIntial)
  const link = {
    click: jest.fn(),
    remove: jest.fn(),
  }
  jest.spyOn(document, 'createElement').mockImplementation(() => link)
  const data_json = {
    data: {},
    xls_report: 'aGVsbG8=',
  }
  const expectedFileName = 'filename'
  const expectedReturn = {
    click: link.click,
    download: `${expectedFileName}.xlsx`,
    href: 'myURL',
    remove: link.remove,
  }
  expect(getParseErrors(data_json, expectedFileName).download).toEqual(
    expectedReturn.download
  )
  expect(getParseErrors(data_json, expectedFileName).href).toEqual(
    expectedReturn.href
  )
  expect(getParseErrors(data_json, expectedFileName).click).toEqual(
    expectedReturn.click
  )
  expect(getParseErrors(data_json, expectedFileName).remove).toEqual(
    expectedReturn.remove
  )
})
