/** @returns {string} A local destination, or the usual landing page. */
export const getLoginDestination = (search = '') => {
  try {
    const destination = new URLSearchParams(search).get('next')
    if (!destination?.startsWith('/') || destination.startsWith('//')) {
      return '/home'
    }

    const url = new URL(destination, window.location.origin)
    const pathname = decodeURIComponent(url.pathname).replace(/\/+$/, '')
    if (
      url.origin !== window.location.origin ||
      destination.includes('\\') ||
      !pathname ||
      pathname.toLowerCase() === '/login'
    ) {
      return '/home'
    }

    return destination
  } catch {
    return '/home'
  }
}
