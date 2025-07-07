import { useEffect, useState, useRef } from 'react'

export function useStickyAboveFooter(offset = 0, minWidth = 0) {
  const [topPosition, setTopPosition] = useState(null)
  const [isVisible, setIsVisible] = useState(true)
  const containerRef = useRef(null)

  useEffect(() => {
    const footer = document.querySelector('footer')
    if (!footer) return

    const updatePosition = () => {
      const footerRect = footer.getBoundingClientRect()
      const scrollY = window.scrollY || window.pageYOffset
      const footerHeight = footer.offsetHeight
      //const top = footerRect.top + scrollY - offset
      const top = footerRect.top + scrollY - offset - footerHeight

      setTopPosition(top)
      setIsVisible(window.innerWidth > minWidth)
    }

    updatePosition()

    const resizeObserver = new ResizeObserver(updatePosition)
    //resizeObserver.observe(document.body)
    resizeObserver.observe(footer)

    window.addEventListener('scroll', updatePosition)
    window.addEventListener('resize', updatePosition)

    return () => {
      resizeObserver.disconnect()
      window.removeEventListener('scroll', updatePosition)
      window.removeEventListener('resize', updatePosition)
    }
  }, [offset, minWidth])

  return { topPosition, isVisible, containerRef }
}
