import React, { useState } from 'react'
import FeedbackModal from './FeedbackModal'
import FeedbackForm from './FeedbackForm'

function Feedback() {
  const supportEmail = 'tanfdata@acf.hhs.gov'
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFeedbackSubmitted, setIsFeedbackSubmitted] = useState(false)

  const handleOpenModal = () => {
    console.log('Opening feedback modal')
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setIsFeedbackSubmitted(false)
  }

  const handleOnFeedbackSubmit = () => {
    setIsFeedbackSubmitted(true)
    console.log('Thank you for your feedback!')
  }

  return (
    <>
      <button
        type="button"
        data-testid="usa-feedback-sticky-button"
        className="usa-button"
        style={{
          position: 'fixed',
          bottom: '0px',
          right: '45px',
          padding: '10px 20px',
          zIndex: isModalOpen ? 'auto' : 1000,
          borderRadius: '0',
        }}
        onClick={handleOpenModal}
      >
        Give Feedback
      </button>
      {isModalOpen && !isFeedbackSubmitted ? (
        <FeedbackModal
          id="feedback-modal"
          title="Tell us how we can improve TDP"
          isOpen={isModalOpen}
          message="Your feedback is important to us! We use it to ensure that the TANF Data Portal is meeting your needs and better serve you and your team."
          onClose={handleCloseModal}
        >
          <div
            style={{
              justifyContent: 'center',
              alignItems: 'center',
              marginTop: '5px',
            }}
          >
            <FeedbackForm onFeedbackSubmit={handleOnFeedbackSubmit} />
          </div>
        </FeedbackModal>
      ) : (
        isModalOpen && (
          <FeedbackModal
            id="feedback-thank-you-modal"
            title="Thank you for your feedback"
            isOpen={isModalOpen}
            message={
              <p>
                Your response has been recorded. If you're encountering an issue
                you need support to resolve please feel free to email us at{' '}
                <a className="usa-link" href={`mailto:${supportEmail}`}>
                  {supportEmail}
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
