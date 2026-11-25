import React, { useRef, useEffect } from 'react'
import PropTypes from 'prop-types'
import Button from '../Button'

const FOCUSABLE_SELECTOR =
  'a[href], button:not([disabled]), textarea:not([disabled]), select:not([disabled]), input:not([type="hidden"]):not([disabled]), [tabindex]:not([tabindex="-1"])'

const Modal = ({
  title,
  message,
  children,
  buttons = [],
  isVisible = false,
  onClose,
  closeOnOutsideClick = false,
}) => {
  const modalRef = useRef(null)

  useEffect(() => {
    if (!isVisible) return undefined

    const returnFocusElement = document.activeElement
    modalRef.current.querySelector('h1').focus()

    return () => {
      returnFocusElement?.focus?.()
    }
  }, [isVisible])

  const onTabPressed = (shiftKey) => {
    const focusableElements = Array.from(
      modalRef.current.querySelectorAll(FOCUSABLE_SELECTOR)
    )
    if (focusableElements.length === 0) return

    const currentIndex = focusableElements.indexOf(document.activeElement)
    let nextIndex = 0

    if (currentIndex !== -1) {
      if (shiftKey) {
        nextIndex =
          (currentIndex - 1 + focusableElements.length) %
          focusableElements.length
      } else {
        nextIndex = (currentIndex + 1) % focusableElements.length
      }
    } else if (shiftKey) {
      nextIndex = focusableElements.length - 1
    }

    focusableElements[nextIndex].focus()
  }

  const onKeyDown = (e) => {
    const { key, shiftKey } = e
    switch (key) {
      case 'Tab':
        onTabPressed(shiftKey)
        e.preventDefault()
        break

      case 'Escape':
        if (onClose) {
          e.preventDefault()
          onClose()
        }
        break

      default:
        break
    }
  }

  const onOverlayClick = (e) => {
    if (closeOnOutsideClick && onClose && e.target === e.currentTarget) {
      onClose()
    }
  }

  return isVisible ? (
    <div
      id="modal"
      className="modal display-block"
      onKeyDown={onKeyDown}
      onClick={onOverlayClick}
      role="presentation"
    >
      <div
        className="modal-content"
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modalHeader"
        tabIndex="-1"
      >
        <h1
          className="font-serif-xl margin-4 margin-bottom-0 text-normal"
          tabIndex="-1"
          id="modalHeader"
          aria-describedby="modalDescription"
        >
          {title}
        </h1>
        {Boolean(message) && (
          <p id="modalDescription" className="margin-4 margin-top-1">
            {message}
          </p>
        )}
        {children && (
          <div
            id={!message ? 'modalDescription' : undefined}
            className="margin-4 margin-top-1"
          >
            {children}
          </div>
        )}
        <div className="margin-x-4 margin-bottom-4">
          {buttons.map((b) => (
            <Button
              key={b.key}
              buttonKey={b.key}
              type="button"
              className="mobile:margin-bottom-1 mobile-lg:margin-bottom-0"
              onClick={b.onClick}
            >
              {b.text}
            </Button>
          ))}
        </div>
      </div>
    </div>
  ) : null
}

Modal.propTypes = {
  title: PropTypes.string,
  message: PropTypes.node,
  children: PropTypes.node,
  buttons: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      onClick: PropTypes.func.isRequired,
    })
  ),
  isVisible: PropTypes.bool,
  onClose: PropTypes.func,
  closeOnOutsideClick: PropTypes.bool,
}

export default Modal
