import React, { useState } from 'react'
import Button from '../Button'
import FeedbackModal from './FeedbackModal'
import FeedbackForm from './FeedbackForm'
import classNames from 'classnames'
import {
  FEEDBACK_MODAL_HEADER,
  FEEDBACK_SUCCESS_RESPONSE_HEADER,
  TANF_SUPPORT_EMAIL,
} from './FeedbackConstants'

function Feedback() {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFeedbackSubmitted, setIsFeedbackSubmitted] = useState(false)

  const handleOpenModal = () => {
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setIsFeedbackSubmitted(false)
  }

  const handleOnFeedbackSubmit = () => {
    setIsFeedbackSubmitted(true)
  }

  return (
    <>
      <Button
        type="button"
        data-testid="usa-feedback-sticky-button"
        className={classNames('usa-button', 'feedback-button', {
          'modal-open': isModalOpen,
        })}
        onClick={handleOpenModal}
      >
        Give Feedback
      </Button>
      {isModalOpen && !isFeedbackSubmitted ? (
        <FeedbackModal
          id="feedback-modal"
          title="Tell us how we can improve TDP"
          isOpen={isModalOpen}
          message={FEEDBACK_MODAL_HEADER}
          onClose={handleCloseModal}
        >
          <div
            style={{
              justifyContent: 'center',
              alignItems: 'center',
              marginTop: '5px',
            }}
          >
            <FeedbackForm
              isGeneralFeedback={true}
              onFeedbackSubmit={handleOnFeedbackSubmit}
            />
          </div>
        </FeedbackModal>
      ) : (
        isModalOpen && (
          <FeedbackModal
            id="feedback-thank-you-modal"
            title={FEEDBACK_SUCCESS_RESPONSE_HEADER}
            isOpen={isModalOpen}
            message={
              <p>
                Your response has been recorded. If you're encountering an issue
                you need support to resolve, please feel free to email us at{' '}
                <a className="usa-link" href={`mailto:${TANF_SUPPORT_EMAIL}`}>
                  {TANF_SUPPORT_EMAIL}
                </a>
                .
              </p>
            }
            onClose={handleCloseModal}
          >
            <div className="margin-x-4 margin-bottom-4">
              <button
                id="feedback-close-button"
                data-testid="feedback-submit-close-button"
                className="usa-button"
                type="button"
                onClick={handleCloseModal}
                style={{ marginTop: '8px' }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    handleCloseModal()
                  }
                }}
              >
                Close
              </button>
            </div>
          </FeedbackModal>
        )
      )}
    </>
  )
}

export default Feedback
