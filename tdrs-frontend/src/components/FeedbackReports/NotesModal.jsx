import React from 'react'
import PropTypes from 'prop-types'
import Modal from '../Modal'

/**
 * NotesModal component displays the full notes associated with a feedback report upload.
 */
function NotesModal({ filename, notes, onClose, isVisible = true }) {
  return (
    <Modal
      title="Notes"
      isVisible={isVisible}
      onClose={onClose}
      closeOnOutsideClick
      buttons={[
        {
          key: '1',
          text: 'Close',
          onClick: onClose,
        },
      ]}
    >
      <div
        className="notes-modal-body"
        role="region"
        aria-label="Report notes"
        tabIndex="0"
      >
        {filename && (
          <p className="margin-0">
            <strong>File:</strong> {filename}
          </p>
        )}
        <hr className="margin-y-2 border-top-1px border-base-lighter" />
        <p className="notes-modal-text margin-0">{notes}</p>
      </div>
    </Modal>
  )
}

NotesModal.propTypes = {
  filename: PropTypes.string,
  notes: PropTypes.string.isRequired,
  onClose: PropTypes.func.isRequired,
  isVisible: PropTypes.bool,
}

export default NotesModal
