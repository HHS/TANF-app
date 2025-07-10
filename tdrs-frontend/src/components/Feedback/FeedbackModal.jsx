import React, { useRef, useEffect, useCallback } from 'react'
import closeIcon from '@uswds/uswds/img/usa-icons/close.svg'
import '../../assets/feedback/Feedback.scss'
import { useFocusTrap } from '../../hooks/useFocusTrap'

const FeedbackModal = ({ id, title, message, children, isOpen, onClose }) => {
  const modalRef = useRef(null)

  useFocusTrap({ containerRef: modalRef, isActive: isOpen })

  // Escape key closes modal here
  const onKeyDown = useCallback(
    (e) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
      }
    },
    [onClose]
  )

  useEffect(() => {
    if (!isOpen || !modalRef.current) return
    const node = modalRef.current
    node.addEventListener('keydown', onKeyDown)
    return () => node.removeEventListener('keydown', onKeyDown)
  }, [isOpen, onKeyDown])

  return isOpen ? (
    <div
      id={id}
      className="usa-modal-overlay feedback-modal-overlay"
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
        className="modal-content feedback-modal-content"
        data-testid="feedback-modal-content"
        ref={modalRef}
        style={{
          width: 'auto',
          height: 'auto',
          borderRadius: '0.5rem',
        }}
        role="presentation"
        onClick={(e) => e.stopPropagation()}
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
            className="usa-modal__close margin-right-4 feedback-modal-close-button"
            aria-label="Close modal"
            style={{ padding: '0', marginBottom: '1px' }}
            onClick={onClose}
          >
            <img src={closeIcon} alt="X" />
          </button>
        </div>
        <div id="feedback-modal-body">
          <p
            id="modalDescription"
            className="font-sans-md font-family-sans margin-4 margin-top-3 margin-bottom-0"
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
