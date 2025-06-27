import React, { useRef, useEffect, useCallback, useState } from 'react'
import '../../assets/feedback/Feedback.scss'
import { useFocusTrap } from 'hooks/useFocusTrap'
import FeedbackForm from './FeedbackForm'

const FeedbackWidget = ({ isOpen, onClose }) => {
  const [isVisible, setIsVisible] = useState(true)
  const widgetRef = useRef(null)

  useFocusTrap({ containerRef: widgetRef, isActive: isOpen })

  const handleFeedbackSubmit = () => {
    // Called when form submits successfully
    setTimeout(() => setIsVisible(false), 1000)
  }

  return isOpen ? (
    <div
      className="feedback-widget"
      ref={widgetRef}
      role="dialog"
      aria-labelledby="feedbackWidgetHeader"
      aria-describedby="feedbackWidgetDesc"
      tabIndex={-1}
    >
      <div className="feedback-widget-content">
        <div className="feedback-widget-header">
          <h1 id="feedbackWidgetHeader" className="font-serif-lg" tabIndex={-1}>
            We'd love your feedback
          </h1>
          <button
            type="button"
            className="feedback-widget-close"
            aria-label="Close feedback widget"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <p id="feedbackWidgetDesc">
          Tell us about your experience with file upload.
        </p>
        <FeedbackForm
          isGeneralFeedback={false} // compact form (no validation banner)
          onFeedbackSubmit={handleFeedbackSubmit} // closes widget after submit
        />
      </div>
    </div>
  ) : null
}

export default FeedbackWidget
