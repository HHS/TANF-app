import { useCallback, useEffect, useRef } from 'react'

console.log('✅ useFocusTrap mock loaded')

const FOCUSABLE_SELECTOR =
  'a[href], button, textarea, select, input:not([type="hidden"]), [tabindex]:not([tabindex="-1"])'

const isVisibleAndFocusable = (el) =>
  el && !el.disabled && el.offsetParent !== null

// Excludes heading with tabindex="-1" from normal focusables
// const isVisibleAndFocusable = (el) =>
//   el &&
//   !el.disabled &&
//   el.offsetParent !== null &&
//   typeof el.focus === 'function' &&
//   !(el.tagName === 'H1' && el.getAttribute('tabindex') === '-1')

export const useFocusTrap = ({ containerRef, isActive }) => {
  console.log('🚨 useFocusTrap invoked', { containerRef, isActive })
  const hasAutoFocused = useRef(false)

  const onKeyDown = useCallback(
    (e) => {
      if (!containerRef?.current || e.key !== 'Tab') return

      let focusableEls = Array.from(
        containerRef.current.querySelectorAll(FOCUSABLE_SELECTOR)
      ).filter(
        (el) =>
          isVisibleAndFocusable(el) &&
          !(el.tagName === 'h1' && el.getAttribute('tabindex') === '-1')
      )

      //const headingEl = containerRef.current.querySelector('h1[tabindex="-1"]')

      // If the heading is focused but not in the list, prepend it
      // const isHeadingFocused = headingEl && headingEl === active
      // if (
      //   isHeadingFocused &&
      //   !focusableEls.includes(headingEl) &&
      //   focusableEls.length === 0
      // ) {
      //   focusableEls = [headingEl]
      // }

      if (focusableEls.length === 0) {
        console.warn('No focusable elements found in modal')
        return
      }

      const active = document.activeElement
      const isActiveInsideModal = containerRef.current.contains(active)
      let index = isActiveInsideModal ? focusableEls.indexOf(active) : -1

      if (index === -1) {
        index = e.shiftKey ? 0 : -1
      }

      const nextIndex = e.shiftKey
        ? (index - 1 + focusableEls.length) % focusableEls.length
        : (index + 1) % focusableEls.length

      e.preventDefault()
      focusableEls[nextIndex]?.focus()
    },
    [containerRef]
  )

  useEffect(() => {
    if (!isActive || !containerRef?.current) return
    const container = containerRef.current
    container.addEventListener('keydown', onKeyDown)

    // Initial focus logic inside timeout (delay render)
    const frame = requestAnimationFrame(() => {
      const alreadyFocused = container.contains(document.activeElement)
      if (hasAutoFocused.current || alreadyFocused) return
      hasAutoFocused.current = true

      const heading = container.querySelector('h1[tabindex="-1"]')
      const focusables = Array.from(
        container.querySelectorAll(FOCUSABLE_SELECTOR)
      ).filter((el) => isVisibleAndFocusable(el))

      console.log('Heading candidate:', heading)
      console.log(
        'Document activeElement BEFORE focus trap:',
        document.activeElement
      )
      console.log(
        '🔍 focusables found:',
        focusables.map((el) => el.outerHTML)
      )
      console.log(
        'Focusables order:',
        focusables.map((el) => el.dataset?.testid || el.tagName)
      )
      console.log('✅ heading focusable:', isVisibleAndFocusable(heading))
      console.log('hasAutoFocused:', hasAutoFocused)

      if (focusables.length === 0) {
        console.warn('No focusable elements found in modal')
        container.focus()
        return
      }

      if (heading && isVisibleAndFocusable(heading)) {
        heading.focus()
        // Manually ensure it's marked focused in jsdom (helpful for tests)
        if (document.activeElement !== heading) {
          heading.focus()
        }
      } else {
        focusables[0].focus()
      }
    })

    return () => {
      cancelAnimationFrame(frame)
      container.removeEventListener('keydown', onKeyDown)
      hasAutoFocused.current = false
    }
  }, [containerRef, isActive, onKeyDown])
}
