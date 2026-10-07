import React, { useCallback, useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import { useFocusTrap } from '../../hooks/useFocusTrap'

/**
 * NotesModal component displays the full notes associated with a feedback report upload.
 */
function NotesModal({ filename, notes, onClose }) {
  const dialogRef = useRef(null)
  const returnFocusRef = useRef(document.activeElement)
  const { onKeyDown: trapKeyDown } = useFocusTrap({
    containerRef: dialogRef,
    isActive: true,
  })

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    const returnFocusElement = returnFocusRef.current
    document.body.style.overflow = 'hidden'

    return () => {
      document.body.style.overflow = previousOverflow
      returnFocusElement?.focus()
    }
  }, [])

  const onKeyDown = useCallback(
    (event) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }
      trapKeyDown(event)
    },
    [onClose, trapKeyDown]
  )

  useEffect(() => {
    const dialog = dialogRef.current
    dialog?.addEventListener('keydown', onKeyDown)

    return () => dialog?.removeEventListener('keydown', onKeyDown)
  }, [onKeyDown])

  return (
    <div className="notes-modal-overlay">
      <section
        ref={dialogRef}
        className="notes-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="notes-modal-title"
        tabIndex="-1"
      >
        <header className="notes-modal-header">
          <h1
            id="notes-modal-title"
            className="font-serif-xl margin-0 text-normal"
            tabIndex="-1"
          >
            Notes
          </h1>
        </header>

        <div className="notes-modal-body">
          {filename && (
            <p className="margin-0">
              <strong>File:</strong> {filename}
            </p>
          )}
          <hr className="margin-y-2 border-top-1px border-base-lighter" />
          <p className="notes-modal-text margin-0">{notes}</p>
        </div>

        <footer className="notes-modal-footer">
          <button type="button" className="usa-button" onClick={onClose}>
            Close
          </button>
        </footer>
      </section>
    </div>
  )
}

NotesModal.propTypes = {
  filename: PropTypes.string,
  notes: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
}

export default NotesModal
