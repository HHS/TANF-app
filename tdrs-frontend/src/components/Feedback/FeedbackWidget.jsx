import React, {
  useRef,
  useEffect,
  useCallback,
  useState,
  useImperativeHandle,
} from 'react'
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
    const widgetRef = useRef(null)

    useFocusTrap({ containerRef: widgetRef, isActive: isOpen })

    // Forward the ref up to parent
    useImperativeHandle(ref, () => widgetRef.current)

    const handleFeedbackSubmit = () => {
      // Called when form submits successfully
      setTimeout(() => {
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
    //   //   // Reset visibility when widget is reopened
    //   if (!isOpen) {
    //     return
    //   }

    //   const widget = widgetRef.current
    //   const footer = document.querySelector('footer')
    //   if (!widget || !footer) return

    //   // Get footer height to position widget just above it
    //   const footerHeight = footer.offsetHeight
    //   // const footerRect = footer.getBoundingClientRect()
    //   // const bottomSpace = window.innerHeight - footerRect.top

    //   // Position widget fixed above footer by setting bottom = footerHeight
    //   widget.style.position = 'relative' // change to relative for correct positioning
    //   //widget.style.bottom = `${footerHeight}px`
    //   widget.style.right = '13.5rem' // keep your right positioning
    // }, [isOpen])

    return isOpen ? (
      <div
        className="feedback-widget"
        ref={widgetRef}
        role="dialog"
        aria-labelledby="feedbackWidgetHeader"
        aria-describedby="feedbackWidgetDesc"
      >
        <div className="feedback-widget-content">
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
              className="margin-right-2 feedback-modal-close-button feedback-widget-modal-close-button"
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
)

export default FeedbackWidget
