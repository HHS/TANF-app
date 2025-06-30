import React, { useRef, useEffect, useCallback, useState } from 'react'
import '../../assets/feedback/Feedback.scss'
import { useFocusTrap } from '../../hooks/useFocusTrap'
import FeedbackForm from './FeedbackForm'
import {
  FRA_DATA_UPLOAD_FEEDBACK_HEADER,
  SSP_MOE_DATA_UPLOAD_FEEDBACK_HEADER,
  TANF_DATA_UPLOAD_FEEDBACK_HEADER,
} from './FeedbackConstants'

const FeedbackWidget = ({ isOpen, onClose, dataType }) => {
  // const [isVisible, setIsVisible] = useState(true)
  const widgetRef = useRef(null)

  useFocusTrap({ containerRef: widgetRef, isActive: isOpen })

  const handleFeedbackSubmit = () => {
    // Called when form submits successfully
    setTimeout(() => {
      //setIsVisible(false)
      onClose?.()
    }, 1000)
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

  // useEffect(() => {
  //   // Reset visibility when widget is reopened
  //   if (isOpen) {
  //     setIsVisible(true)
  //   }
  // }, [isOpen])

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
          <h5 id="feedbackWidgetHeader" className="font-serif-lg" tabIndex={-1}>
            {getFeedbackWidgetHeader()}
          </h5>
          <button
            data-testid="feedback-widget-close-button"
            type="button"
            className="usa-modal__close margin-right-4 feedback-modal-close-button"
            aria-label="Close feedback widget"
            onClick={onClose}
          >
            X
          </button>
        </div>
        <FeedbackForm
          isGeneralFeedback={false} // compact form (no validation banner)
          onFeedbackSubmit={handleFeedbackSubmit} // closes widget after submit
        />
      </div>
    </div>
  ) : null
}

export default FeedbackWidget
