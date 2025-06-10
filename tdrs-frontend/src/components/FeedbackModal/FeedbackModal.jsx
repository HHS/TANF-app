import React, { useRef, useEffect } from 'react'

const FeedbackModal = ({
  title,
  message,
  children,
  isOpen,
  onClose,
  modalWidth,
  modalHeight,
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
    <div id="feedback-modal" className="usa-modal-overlay" role="presentation">
      <div
        className="modal-content"
        ref={modalRef}
        style={{
          width: modalWidth,
          height: modalHeight,
          justifyContent: 'center',
          alignItems: 'center',
          borderRadius: '0.5rem',
        }}
      >
        <div id="feedback-modal-header-container">
          <h1
            className="font-serif-xl margin-4 margin-bottom-0 text-normal"
            tabIndex={-1}
            id="feedbackModalHeader"
            aria-describedby="modalDescription"
          >
            {title}
          </h1>
          <button
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
