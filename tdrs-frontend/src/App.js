import React, { useState } from 'react'
import GovBanner from './components/GovBanner'
import Routes from './components/Routes'
import { Alert } from './components/Alert'
import Header from './components/Header'
import Footer from './components/Footer'
import FeedbackForm from 'components/FeedbackForm'
import FeedbackModal from 'components/FeedbackModal'

/**
 * The root component
 *
 * Renders the Gov Banner on every page.
 *
 * Renders the Alert component which will show or hide alerts
 *
 * Renders Routes and all its children
 */
function App() {
  const supportEmail = 'tanfdata@acf.hhs.gov'

  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isFeedbackSubmitted, setIsFeedbackSubmitted] = useState(false)

  const handleOpenModal = () => {
    console.log('Opening feedback modal')
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  const handleOnFeedbackSubmit = () => {
    setIsFeedbackSubmitted(true)
    console.log('Thank you for your feedback!')
  }

  return (
    <>
      <a
        className="usa-skipnav"
        href="#main-content"
        onKeyPress={(e) => {
          if (e.charCode === 32) {
            window.location.href = '#main-content'
          }
        }}
      >
        Skip to main content
      </a>
      <GovBanner />
      <Header />
      <Alert />
      <main id="main-content">
        <Routes />
      </main>
      <Footer />
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
          title="Tell us how we can improve TDP"
          isOpen={isModalOpen}
          message="Your feedback is important to us! We use it to ensure that the TANF Data Portal is meeting your needs and better serve you and your team."
          modalWidth={'53.75rem'}
          modalHeight={'auto'}
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
        <FeedbackModal
          title="Thank you for your feedback"
          isOpen={isModalOpen}
          message={
            <p>
              Your response has been recorded. If you're encountering an issue
              you need support to resolve please feel free to email us at{' '}
              <a className="usa-link" href="mailto:tanfdata@acf.hhs.gov">
                {supportEmail}
              </a>
              .
            </p>
          }
          modalWidth={'53.75rem'}
          modalHeight={'auto'}
          onClose={handleCloseModal}
        >
          <div className="margin-x-4 margin-bottom-4">
            <button
              id="feedback-submit-button"
              className="usa-button"
              type="button"
              onClick={handleCloseModal}
              style={{ marginTop: '8px' }}
            >
              Close
            </button>
          </div>
        </FeedbackModal>
      )}
    </>
  )
}

export default App
