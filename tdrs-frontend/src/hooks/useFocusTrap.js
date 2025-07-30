import { useEffect, useCallback, useRef } from 'react'

const FOCUSABLE_SELECTOR =
  'a[href], button, textarea, select, input:not([type="hidden"]), [tabindex]:not([tabindex="-1"])'

export function useFocusTrap({ containerRef, isActive }) {
  const lastFocusedEl = useRef(null)
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
        // Manually ensure it's marked focused in jsdom (helpful for tests)
        if (document.activeElement !== headingEl) {
          headingEl.focus()
        }
      } else if (focusables.length > 0) {
        focusables[0].focus()
      } else {
        if (container) {
          container.focus()
        }
      }
    })

    return () => {
      hasAutoFocused.current = false
    }
  }, [isActive, containerRef])

  // Reset on close
  useEffect(() => {
    if (!isActive) {
      hasAutoFocused.current = false
    }
  }, [isActive])

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
          !(el.tagName === 'h1' && el.getAttribute('tabindex') === '-1')
      )

      const headingEl = containerRef.current.querySelector('h1[tabindex="-1"]')
      const activeEl = document.activeElement
      const lastEl = lastFocusedEl.current

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
      let currentIdx = isActiveInside ? focusableElements.indexOf(activeEl) : -1

      // If the current activeEl is not found (e.g. removed), fall back to last known focused element
      if (currentIdx === -1 && lastEl && focusableElements.includes(lastEl)) {
        currentIdx = focusableElements.indexOf(lastEl)
      }

      const nextIdx = shiftKey
        ? (currentIdx - 1 + focusableElements.length) % focusableElements.length
        : (currentIdx + 1) % focusableElements.length

      focusableElements[nextIdx].focus()
    },
    [containerRef]
  )

  // Handle keydown event
  const onKeyDown = useCallback(
    (e) => {
      if (e.key === 'Tab') {
        if (containerRef.current?.contains(document.activeElement)) {
          lastFocusedEl.current = document.activeElement
        }
        e.preventDefault()
        onTabPressed(e.shiftKey)
      }
    },
    [containerRef, onTabPressed]
  )

  // Return the keydown handler
  return { onKeyDown }
}
