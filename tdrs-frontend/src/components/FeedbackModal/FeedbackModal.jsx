import React, { useRef, useEffect, useCallback } from 'react'

const FOCUSABLE_SELECTOR =
  'a[href], button, textarea, select, [tabindex]:not([tabindex="-1"])'

const FeedbackModal = ({ id, title, message, children, isOpen, onClose }) => {
  const modalRef = useRef(null)
  const hasAutoFocused = useRef(false)

  useEffect(() => {
    if (isOpen && modalRef.current && !hasAutoFocused.current) {
      const modalEl = modalRef.current
      const headingEl = modalEl.querySelector('h1')

      const timeoutId = setTimeout(() => {
        if (!modalEl) return
        const focusableEls = modalEl.querySelectorAll(FOCUSABLE_SELECTOR)
        const focusables = Array.from(focusableEls).filter(
          (el) => !el.disabled && el.offsetParent !== null
        )

        // focus on heading
        if (headingEl) {
          headingEl.focus()
          // Manually ensure it's marked focused in jsdom (helpful for tests)
          if (document.activeElement !== headingEl) {
            headingEl.focus()
          }
        } else if (focusables.length > 0) {
          // If no heading, fall back to first focusable
          focusables[0].focus()
        } else {
          if (modalEl) {
            // Fallback: focus modal itself
            modalEl.focus()
          }
        }
        hasAutoFocused.current = true
      }, 0)

      return () => clearTimeout(timeoutId)
    }
  }, [isOpen, modalRef])

  useEffect(() => {
    if (!isOpen) {
      hasAutoFocused.current = false
    }
  }, [isOpen])

  const onTabPressed = useCallback(
    (shiftKey = false) => {
      if (!modalRef.current) return

      let focusableElements = Array.from(
        modalRef.current.querySelectorAll(FOCUSABLE_SELECTOR)
      ).filter(
        (el) =>
          !el.disabled &&
          el.offsetParent !== null &&
          !(el.tagName === 'h1' && el.getAttribute('tabindex') === '-1')
      )

      const headingEl = modalRef.current.querySelector('h1[tabindex="-1"]')
      const activeEl = document.activeElement

      // If the heading is focused but not in the list, prepend it
      const isHeadingFocused = headingEl && headingEl === activeEl
      if (
        headingEl &&
        isHeadingFocused &&
        !focusableElements.includes(headingEl)
      ) {
        focusableElements = [headingEl, ...focusableElements]
      }

      if (focusableElements.length === 0) {
        console.warn('No focusable elements found in modal')
        return
      }

      console.log(
        'Focusable elements:',
        focusableElements.map((el) => el.dataset.testid || el.outerHTML)
      )
      const isActiveInsideModal = modalRef.current.contains(activeEl)
      const currentIdx = isActiveInsideModal
        ? focusableElements.indexOf(activeEl)
        : -1
      const nextIdx =
        currentIdx === -1
          ? 0
          : shiftKey
            ? (currentIdx - 1 + focusableElements.length) %
              focusableElements.length
            : (currentIdx + 1) % focusableElements.length

      console.log(
        'Active element:',
        activeEl.dataset.testid || activeEl.outerHTML
      )
      console.log('Tab pressed: currentIdx', currentIdx, 'nextIdx', nextIdx)
      focusableElements[nextIdx].focus()
    },
    [modalRef]
  )

  const onKeyDown = useCallback(
    (e) => {
      if (e.key === 'Tab') {
        e.preventDefault()
        onTabPressed(e.shiftKey)
      } else if (e.key === 'Escape') {
        e.preventDefault()
      }
    },
    [onTabPressed]
  )

  return isOpen ? (
    <div
      id={id}
      className="usa-modal-overlay"
      data-testid="feedback-modal-overlay"
      tabIndex={-1}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      role="presentation"
      onKeyDown={onKeyDown}
    >
      <div
        className="modal-content"
        data-testid="feedback-modal-content"
        ref={modalRef}
        tabIndex={-1}
        style={{
          width: 'auto',
          height: 'auto',
          borderRadius: '0.5rem',
        }}
      >
        <div id="feedback-modal-header-container">
          <h1
            data-testid="feedback-modal-header"
            className="font-serif-xl margin-4 margin-bottom-0 text-normal"
            tabIndex={-1}
            id="feedbackModalHeader"
            aria-describedby="modalDescription"
          >
            {title}
          </h1>
          <button
            data-testid="modal-close-button"
            type="button"
            className="usa-modal__close margin-right-4 margin-bottom-0"
            style={{
              background: 'none',
              border: 'none',
              fontSize: '1.25rem',
              fontWeight: 'bold',
              lineHeight: '1',
              padding: '0',
              marginBottom: '1px',
              cursor: 'pointer',
            }}
            aria-label="Close modal"
            onClick={onClose}
          >
            X
          </button>
        </div>
        <div id="feedback-modal-body">
          <p
            id="modalDescription"
            className="font-serif-md margin-4 margin-top-3 margin-bottom-0"
            style={{ lineHeight: '1.25' }}
          >
            {message}
          </p>
          {children}
        </div>
      </div>
    </div>
  ) : null
}

export default FeedbackModal
