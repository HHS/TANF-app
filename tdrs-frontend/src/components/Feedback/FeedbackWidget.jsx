import React, { useRef, useEffect, useState, useImperativeHandle } from 'react'
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
      setIsFeedbackSubmitted(true)
      setShowSpinner(true) // Show spinner while processing
    }

    // Close and reset after 5 seconds
    useEffect(() => {
      if (!isFeedbackSubmitted) return

      const timer = setTimeout(() => {
        setShowSpinner(false)
        setIsFeedbackSubmitted(false)
        onClose?.()
      }, 5000)

      return () => clearTimeout(timer)
    }, [isFeedbackSubmitted, onClose])

    // Pick the correct widget header based on dataType
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
        style={isFeedbackSubmitted ? { paddingBottom: '1rem' } : {}}
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
                  className="font-serif-sm margin-2 text-normal"
                  tabIndex={-1}
                  aria-describedby="widgetDesc"
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
                isGeneralFeedback={false}
                onFeedbackSubmit={handleFeedbackSubmit}
              />
            </>
          ) : (
            <div className="feedback-widget-thank-you-header">
              <p
                id="feedbackWidgetHeader"
                className="font-serif-xs margin-left-0 text-normal"
                tabIndex={-1}
              >
                Thank you for your feedback!
              </p>
              {showSpinner && <span className="spinner" aria-label="Loading" />}
              <button
                data-testid="feedback-widget-thank-you-close-button"
                type="button"
                className="usa-modal__close feedback-modal-close-button"
                aria-label="Close feedback widget"
                style={{
                  padding: '0',
                  alignSelf: 'center',
                }}
                onClick={onClose}
              >
                <img
                  src={closeIcon}
                  alt="X"
                  style={{ width: '14px', height: 'auto' }}
                />
              </button>
            </div>
          )}
        </div>
      </div>
    ) : null
  }
)

export default FeedbackWidget
