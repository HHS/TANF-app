import React, { useRef, useEffect } from 'react'
import Button from '../Button'

const Modal = ({ title, message, buttons = [], isVisible = false }) => {
  const modalRef = useRef(null)
  useEffect(
    () =>
      isVisible && modalRef && modalRef.current
        ? modalRef.current.querySelector('h1').focus()
        : undefined,
    [isVisible, modalRef, buttons]
  )

  const onTabPressed = (shiftKey = false) => {
    const selectedButton = document.activeElement
    const selectedButtonKey = selectedButton
      ? selectedButton.getAttribute('buttonkey')
      : null

    let nextButtonIndex = 0

    if (selectedButtonKey !== null) {
      const selectedButtonIndex = buttons.findIndex(
        (b) => b.key === selectedButtonKey
      )

      if (shiftKey) {
        // go backward
        nextButtonIndex =
          selectedButtonIndex >= 0
            ? selectedButtonIndex - 1
            : buttons.length - 1
      } else {
        nextButtonIndex =
          selectedButtonIndex < buttons.length - 1 ? selectedButtonIndex + 1 : 0
      }
    }

    const nextButtonKey = buttons[nextButtonIndex].key
    const nextButton = modalRef.current.querySelector(
      `button[buttonkey="${nextButtonKey}"]`
    )
    nextButton.focus()
  }

  const onKeyDown = (e) => {
    const { key, shiftKey } = e

    switch (key) {
      case 'Tab':
        onTabPressed(shiftKey)
        e.preventDefault()
        break

      default:
        break
    }

    return
  }

  return isVisible ? (
    <div
      id="modal"
      className="modal display-block"
      onKeyDown={onKeyDown}
      role="presentation"
    >
      <div className="modal-content" ref={modalRef}>
        <h1
          className="font-serif-xl margin-4 margin-bottom-0 text-normal"
          tabIndex="-1"
          id="modalHeader"
          aria-describedby="modalDescription"
        >
          {title}
        </h1>
        <p id="modalDescription" className="margin-4 margin-top-1">
          {message}
        </p>
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

export default Modal
