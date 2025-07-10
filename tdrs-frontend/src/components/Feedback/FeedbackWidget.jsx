import React, { useRef, useState, useImperativeHandle } from 'react'
import closeIcon from '@uswds/uswds/img/usa-icons/close.svg'
import '../../assets/feedback/Feedback.scss'
import { useFocusTrap } from '../../hooks/useFocusTrap'
import FeedbackForm from './FeedbackForm'
import {
  FRA_DATA_UPLOAD_FEEDBACK_HEADER,
  SSP_MOE_DATA_UPLOAD_FEEDBACK_HEADER,
  TANF_DATA_UPLOAD_FEEDBACK_HEADER,
} from './FeedbackConstants'

const FeedbackWidget = React.forwardRef(
  ({ isOpen, onClose, dataType }, ref) => {
    const [showSpinner, setShowSpinner] = useState(true)
    const [isFeedbackSubmitted, setIsFeedbackSubmitted] = useState(false)
    const widgetRef = useRef(null)

    useFocusTrap({ containerRef: widgetRef, isActive: isOpen })

    // Forward the ref up to parent
    useImperativeHandle(ref, () => widgetRef.current)

    const handleFeedbackSubmit = () => {
      // Called when form submits successfully
      setIsFeedbackSubmitted(true)
      setShowSpinner(true) // Show spinner while processing

      const timer = setTimeout(() => {
        setShowSpinner(false) // Hide spinner after processing
        onClose?.()
      }, 5000) // Close after 5 seconds

      setIsFeedbackSubmitted(false) // Reset for next use
      return () => clearTimeout(timer)
    }

    const getFeedbackWidgetHeader = () => {
      if (dataType === 'tanf') {
        return TANF_DATA_UPLOAD_FEEDBACK_HEADER
      } else if (dataType === 'ssp-moe') {
        return SSP_MOE_DATA_UPLOAD_FEEDBACK_HEADER
      } else {
        return FRA_DATA_UPLOAD_FEEDBACK_HEADER
      }
    }

    return isOpen ? (
      <div
        className="feedback-widget"
        ref={widgetRef}
        role="dialog"
        aria-labelledby="feedbackWidgetHeader"
        aria-describedby="feedbackWidgetDesc"
      >
        <div className="feedback-widget-content">
          {!isFeedbackSubmitted ? (
            <>
              <div className="feedback-widget-header">
                <p
                  id="feedbackWidgetHeader"
                  className="font-serif-sm"
                  tabIndex={-1}
                >
                  {getFeedbackWidgetHeader()}
                </p>
                <button
                  data-testid="feedback-widget-close-button"
                  type="button"
                  className="usa-modal__close feedback-modal-close-button"
                  aria-label="Close feedback widget"
                  style={{
                    padding: '0',
                    marginBottom: '3px',
                    alignSelf: 'unset',
                  }}
                  onClick={onClose}
                >
                  <img src={closeIcon} alt="X" />
                </button>
              </div>
              <FeedbackForm
                isGeneralFeedback={false} // compact form (no validation banner)
                onFeedbackSubmit={handleFeedbackSubmit} // closes widget after submit
              />
            </>
          ) : (
            <div className="feedback-widget-header">
              <p
                id="feedbackWidgetHeader"
                className="font-serif-sm"
                tabIndex={-1}
              >
                Thank you for your feedback!
              </p>
              {showSpinner && <span className="spinner" aria-label="Loading" />}
            </div>
          )}
        </div>
      </div>
    ) : null
  }
)

export default FeedbackWidget
