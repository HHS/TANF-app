import { renderHook, act } from '@testing-library/react'
import { useFooterHeight } from './useFooterHeight'

describe('useFooterHeight', () => {
  beforeEach(() => {
    // Create a mock footer element
    const footer = document.createElement('footer')
    Object.defineProperty(footer, 'offsetHeight', {
      configurable: true,
      value: 100,
    })
    document.body.appendChild(footer)
  })

  afterEach(() => {
    document.body.innerHTML = ''
    jest.clearAllMocks()
  })

  it('returns the correct footer height without offset', () => {
    const { result } = renderHook(() => useFooterHeight())
    expect(result.current.footerHeight).toBe(100)
  })

  it('returns the correct footer height with offset', () => {
    const { result } = renderHook(() => useFooterHeight(20))
    expect(result.current.footerHeight).toBe(120)
  })

  it('updates the height on window resize', () => {
    const { result } = renderHook(() => useFooterHeight())

    // Change the footer height dynamically
    const footer = document.querySelector('footer')
    Object.defineProperty(footer, 'offsetHeight', {
      configurable: true,
      value: 150,
    })

    act(() => {
      window.dispatchEvent(new Event('resize'))
    })

    expect(result.current.footerHeight).toBe(150)
  })
})
