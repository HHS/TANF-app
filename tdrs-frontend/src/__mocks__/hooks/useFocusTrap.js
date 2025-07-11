import { useEffect } from 'react'

console.log('✅ useFocusTrap mock loaded')

const FOCUSABLE_SELECTOR =
  'a[href], button, textarea, select, input:not([type="hidden"]), [tabindex]:not([tabindex="-1"])'

export const useFocusTrap = ({ containerRef, isActive }) => {
  console.log('🚨 useFocusTrap invoked', { containerRef, isActive })

  useEffect(() => {
    if (!isActive || !containerRef?.current) return

    const container = containerRef.current

    // Initial focus on heading or first focusable
    const heading = container.querySelector('h1[tabindex="-1"]')
    const focusables = Array.from(
      container.querySelectorAll(FOCUSABLE_SELECTOR)
    ).filter((el) => !el.disabled && el.offsetParent !== null)

    if (heading && heading.offsetParent !== null) {
      heading.focus()
    } else if (focusables.length > 0) {
      focusables[0].focus()
    } else {
      container.focus()
      console.warn('No focusable elements found in modal')
    }

    const onKeyDown = (e) => {
      if (e.key !== 'Tab') return

      e.preventDefault()

      let focusableEls = Array.from(
        container.querySelectorAll(FOCUSABLE_SELECTOR)
      ).filter((el) => !el.disabled && el.offsetParent !== null)

      if (focusableEls.length === 0) {
        console.warn('No focusable elements found in modal')
        container.focus()
        return
      }

      const active = document.activeElement
      let index = focusableEls.indexOf(active)

      // Fallback if active element is gone or not in list
      if (index === -1) {
        console.warn('Active element not found in focusables, falling back')
        focusableEls[0].focus()
        return
      }

      const nextIndex = e.shiftKey
        ? (index - 1 + focusableEls.length) % focusableEls.length
        : (index + 1) % focusableEls.length

      focusableEls[nextIndex]?.focus()
    }

    container.addEventListener('keydown', onKeyDown)

    return () => {
      container.removeEventListener('keydown', onKeyDown)
    }
  }, [containerRef, isActive])
}
