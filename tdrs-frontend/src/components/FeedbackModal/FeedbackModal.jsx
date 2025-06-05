import React, { useRef, useEffect } from 'react'
import Button from '../Button'

const FeedbackModal = ({
  title,
  message,
  children,
  isOpen = false,
  onClose,
}) => {
  const modalRef = useRef(null)
  useEffect(
    () =>
      isOpen && modalRef && modalRef.current
        ? modalRef.current.querySelector('h1').focus()
        : undefined,
    [isOpen, modalRef]
  )

  return isOpen ? (
    <div id="modal" className="modal display-block" role="presentation">
      <div className="modal-content" ref={modalRef}>
        <div id="modal-header">
          <h1
            className="font-serif-xl margin-4 margin-bottom-0 text-normal"
            tabIndex="-1"
            id="modalHeader"
            aria-describedby="modalDescription"
          >
            {title}
          </h1>
          <button
            type="button"
            className="usa-modal__close"
            aria-label="Close modal"
            onClick={onClose}
          >
            X
          </button>
        </div>
        <div id="modal-body">
          <p id="modalDescription" className="margin-4 margin-top-1">
            {message}
          </p>
          {children}
        </div>
        <div className="margin-x-4 margin-bottom-4">
          <button
            type="button"
            className="mobile:margin-bottom-1 mobile-lg:margin-bottom-0"
            onClick={() => console.log('Feedback submitted!')}
          >
            Send Feedback
          </button>
        </div>
      </div>
    </div>
  ) : null
}

export default FeedbackModal
