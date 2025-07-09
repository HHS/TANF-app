import { useEffect, useState } from 'react'

export function useFooterHeight(offset = 0) {
  const [footerHeight, setFooterHeight] = useState(0)

  useEffect(() => {
    const updateHeight = () => {
      const footer = document.querySelector('footer')
      if (footer) {
        setFooterHeight(footer.offsetHeight + offset)
      }
    }

    updateHeight()
    window.addEventListener('resize', updateHeight)

    return () => window.removeEventListener('resize', updateHeight)
  }, [offset])

  return { footerHeight }
}
