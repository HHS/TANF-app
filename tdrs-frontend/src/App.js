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
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleOpenModal = () => {
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
  }

  const handleFeedbackSubmit = () => {
    setIsModalOpen(false)
    alert('Thank you for your feedback!')
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
        className="usa-menu-btn"
        style={{
          position: 'fixed',
          right: '20px',
          cursor: 'pointer',
          border: 'none',
          borderRadius: '5px',
          padding: '10px 20px',
          zIndex: 1000,
        }}
        onClick={handleOpenModal}
      >
        Feedback
      </button>
      {isModalOpen && (
        <FeedbackModal
          title="Tell us how we can improve TDP"
          isOpen={isModalOpen}
          message="Your feedback is important to us! We use it to ensure that the TANF Data Portal is meeting your needs and better serve you and your team."
          onClose={handleCloseModal}
        >
          <div style={{ marginTop: '10px' }}>
            <h6>Fields marked with an asterisk (*) are required.</h6>
            <br />
            <FeedbackForm onFeedbackSubmit={handleFeedbackSubmit} />
          </div>
        </FeedbackModal>
      )}
    </>
  )
}

export default App
