import { useEffect, useCallback, useRef } from 'react'

const FOCUSABLE_SELECTOR =
  'a[href], button, textarea, select, input:not([type="hidden"]), [tabindex]:not([tabindex="-1"])'

export function useFocusTrap({ containerRef, isActive }) {
  const hasAutoFocused = useRef(false)

  // Focus first focusable or heading when active
  useEffect(() => {
    if (!isActive || !containerRef?.current) return

    const container = containerRef.current

    requestAnimationFrame(() => {
      const alreadyFocused = container.contains(document.activeElement)

      if (hasAutoFocused.current || alreadyFocused) return

      hasAutoFocused.current = true
      const headingEl = container.querySelector('h1[tabindex="-1"]')
      const focusableEls = container.querySelectorAll(FOCUSABLE_SELECTOR)
      const focusables = Array.from(focusableEls).filter(
        (el) => !el.disabled && el.offsetParent !== null
      )

      if (headingEl) {
        headingEl.focus()
        if (document.activeElement !== headingEl) {
          headingEl.focus()
        }
      } else if (focusables.length > 0) {
        focusables[0].focus()
      } else {
        container.focus()
      }
    })

    return () => {
      hasAutoFocused.current = false
    }
  }, [isActive, containerRef])

  // Handle tab key to cycle focus
  const onTabPressed = useCallback(
    (shiftKey = false) => {
      if (!containerRef.current) return

      let focusableElements = Array.from(
        containerRef.current.querySelectorAll(FOCUSABLE_SELECTOR)
      ).filter(
        (el) =>
          !el.disabled &&
          el.offsetParent !== null &&
          !(el.tagName === 'H1' && el.getAttribute('tabindex') === '-1')
      )

      const headingEl = containerRef.current.querySelector('h1[tabindex="-1"]')
      const activeEl = document.activeElement

      const isHeadingFocused = headingEl && headingEl === activeEl
      if (
        headingEl &&
        isHeadingFocused &&
        !focusableElements.includes(headingEl)
      ) {
        focusableElements = [headingEl, ...focusableElements]
      }

      if (focusableElements.length === 0) {
        console.warn('No focusable elements found in container')
        return
      }

      const isActiveInside = containerRef.current.contains(activeEl)
      const currentIdx = isActiveInside
        ? focusableElements.indexOf(activeEl)
        : -1

      const nextIdx =
        currentIdx === -1
          ? 0
          : shiftKey
            ? (currentIdx - 1 + focusableElements.length) %
              focusableElements.length
            : (currentIdx + 1) % focusableElements.length

      focusableElements[nextIdx].focus()
    },
    [containerRef]
  )

  // Handle keydown event
  const onKeyDown = useCallback(
    (e) => {
      if (e.key === 'Tab') {
        e.preventDefault()
        onTabPressed(e.shiftKey)
      }
    },
    [onTabPressed]
  )

  // Attach keydown listener if active
  useEffect(() => {
    if (!isActive || !containerRef.current) return

    const node = containerRef.current
    node.addEventListener('keydown', onKeyDown)

    return () => {
      node.removeEventListener('keydown', onKeyDown)
    }
  }, [isActive, onKeyDown, containerRef])
}
