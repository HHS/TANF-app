import { getLoginDestination } from './loginRedirect'

describe('login destinations', () => {
  it.each([
    '/data-files?type=tanf',
    '/fra-data-files/2026/1?type=fra#history',
    '/profile',
    '/feedback-reports?name=a%26b%2Bc#reports',
  ])('preserves the full local destination %s', (destination) => {
    expect(
      getLoginDestination(new URLSearchParams({ next: destination }).toString())
    ).toBe(destination)
  })

  it('defaults to home without a destination', () => {
    expect(getLoginDestination()).toBe('/home')
  })
  it.each([
    '',
    'https://example.com/data-files',
    '//example.com/data-files',
    '///example.com',
    '/\\example.com',
    '/\n/example.com',
    // eslint-disable-next-line no-script-url -- Verify script URLs are rejected.
    'javascript:alert(1)',
    'data-files',
    '/',
    '/?type=tanf',
    '/login',
    '/login/?next=/profile',
    '/LOGIN',
    '/%6cogin',
    '/data-files/../login',
    '/profile/..',
    '/%invalid',
  ])('rejects unsafe or looping destinations: %s', (destination) => {
    expect(
      getLoginDestination(new URLSearchParams({ next: destination }).toString())
    ).toBe('/home')
  })
})
