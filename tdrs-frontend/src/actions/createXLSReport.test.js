import { getParseErrors } from './createXLSReport'

it('should create a link to download an XLS report', () => {
  const data = 'aGVsbG8='
  // atob is not available in jest
  global.URL.createObjectURL = jest.fn(() => 'myURL')
  const expectedReturn = 'http://localhost/myURL'
  expect(String(getParseErrors(data, 'file'))).toEqual(expectedReturn)
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
  const data = 'aGVsbG8='
  const expectedFileName = 'filename'
  const expectedReturn = {
    click: link.click,
    download: `${expectedFileName}.xlsx`,
    href: 'myURL',
    remove: link.remove,
  }
  expect(getParseErrors(data, expectedFileName).download).toEqual(
    expectedReturn.download
  )
  expect(getParseErrors(data, expectedFileName).href).toEqual(
    expectedReturn.href
  )
  expect(getParseErrors(data, expectedFileName).click).toEqual(
    expectedReturn.click
  )
  expect(getParseErrors(data, expectedFileName).remove).toEqual(
    expectedReturn.remove
  )
})
