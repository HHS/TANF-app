import { downloadBlob } from './fileDownload'

describe('fileDownload', () => {
  describe('downloadBlob', () => {
    let mockUrl
    let mockLink
    let originalCreateObjectURL
    let originalRevokeObjectURL
    let originalCreateElement
    let originalAppendChild
    let originalRemoveChild

    beforeEach(() => {
      mockUrl = 'blob:http://localhost:3000/mock-blob-url'
      mockLink = {
        href: '',
        setAttribute: jest.fn(),
        click: jest.fn(),
      }

      originalCreateObjectURL = window.URL.createObjectURL
      originalRevokeObjectURL = window.URL.revokeObjectURL
      originalCreateElement = document.createElement
      originalAppendChild = document.body.appendChild
      originalRemoveChild = document.body.removeChild

      window.URL.createObjectURL = jest.fn(() => mockUrl)
      window.URL.revokeObjectURL = jest.fn()
      document.createElement = jest.fn(() => mockLink)
      document.body.appendChild = jest.fn()
      document.body.removeChild = jest.fn()
    })

    afterEach(() => {
      window.URL.createObjectURL = originalCreateObjectURL
      window.URL.revokeObjectURL = originalRevokeObjectURL
      document.createElement = originalCreateElement
      document.body.appendChild = originalAppendChild
      document.body.removeChild = originalRemoveChild
    })

    it('creates a blob URL from the provided blob', () => {
      const blob = new Blob(['test content'])
      downloadBlob(blob, 'test.zip')

      expect(window.URL.createObjectURL).toHaveBeenCalledWith(expect.any(Blob))
    })

    it('creates an anchor element with correct attributes', () => {
      const blob = new Blob(['test content'])
      downloadBlob(blob, 'test.zip')

      expect(document.createElement).toHaveBeenCalledWith('a')
      expect(mockLink.href).toBe(mockUrl)
      expect(mockLink.setAttribute).toHaveBeenCalledWith('download', 'test.zip')
    })

    it('appends link to body, clicks it, and removes it', () => {
      const blob = new Blob(['test content'])
      downloadBlob(blob, 'test.zip')

      expect(document.body.appendChild).toHaveBeenCalledWith(mockLink)
      expect(mockLink.click).toHaveBeenCalled()
      expect(document.body.removeChild).toHaveBeenCalledWith(mockLink)
    })

    it('revokes the blob URL to free memory', () => {
      const blob = new Blob(['test content'])
      downloadBlob(blob, 'test.zip')

      expect(window.URL.revokeObjectURL).toHaveBeenCalledWith(mockUrl)
    })
  })
})
