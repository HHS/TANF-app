import React, { useRef, useEffect } from 'react'

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
          <br />
          {children}
        </div>
      </div>
    </div>
  ) : null
}

export default FeedbackModal
