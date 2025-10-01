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
    const [isFocusTrapActive, setIsFocusTrapActive] = useState(false)
    const [showSpinner, setShowSpinner] = useState(false)
    const [isFeedbackSubmitted, setIsFeedbackSubmitted] = useState(false)

    const timerRef = useRef(null)
    const widgetRef = useRef(null)
    const headerRef = useRef(null)
    const thankYouHeadingRef = useRef(null)
    const { onKeyDown } = useFocusTrap({
      containerRef: widgetRef,
      isActive: isFocusTrapActive,
    })

    // Forward the ref up to parent
    useImperativeHandle(ref, () => widgetRef.current)

    const handleFeedbackSubmit = () => {
      setIsFeedbackSubmitted(true)
      setShowSpinner(true)
    }

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsFocusTrapActive(false)
        onClose?.()
      }
      onKeyDown?.(e) // Trap Tab if active
    }

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

    const handleWidgetClick = (event) => {
      if (!widgetRef.current) return

      const isClickFromOutside = !widgetRef.current.contains(event.target)

      if (isClickFromOutside) {
        setIsFocusTrapActive(true)
        headerRef.current?.focus()
      }
    }

    useEffect(() => {
      const handleClickOutside = (event) => {
        if (widgetRef.current && !widgetRef.current.contains(event.target)) {
          setIsFocusTrapActive(false)
        }
      }
      document.addEventListener('mousedown', handleClickOutside)
      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
      }
    }, [])

    const handleRequestSuccess = () => {
      // Focus the thank-you heading once the view updates
      setTimeout(() => {
        thankYouHeadingRef.current?.focus()
      }, 0)

      // Then schedule widget closure
      timerRef.current = setTimeout(() => {
        setShowSpinner(false)
        setIsFeedbackSubmitted(false)
        onClose?.()
      }, 3000)
    }

    const handleRequestError = () => {
      // TODO: we may want to add in a signal for the user to know their feedback submission failed
      // TODO: example could be if error happens change the thank you modal color to red right before it closes
      setShowSpinner(false)
      setIsFeedbackSubmitted(false)
      onClose?.()
    }

    useEffect(() => {
      return () => clearTimeout(timerRef.current)
    }, [])

    return isOpen ? (
      // eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions
      <div
        className="feedback-widget"
        data-testId="feedback-widget"
        style={isFeedbackSubmitted ? { paddingBottom: '1rem' } : {}}
        ref={widgetRef}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby="feedbackWidgetHeader"
        aria-describedby="feedbackWidgetDesc"
        onClick={handleWidgetClick}
        onKeyDown={handleKeyDown}
      >
        <div className="feedback-widget-content">
          {!isFeedbackSubmitted ? (
            <>
              <div className="feedback-widget-header">
                <p
                  ref={headerRef}
                  id="feedbackWidgetHeader"
                  className="font-serif-sm margin-2 text-normal"
                  tabIndex={-1}
                  aria-describedby="widgetDesc"
                  onMouseDown={(e) => e.preventDefault()}
                  role="presentation"
                  aria-hidden="true"
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
              <span id="feedbackWidgetDesc" className="usa-sr-only">
                {`How was your experience uploading ${dataType} data? Navigate to the end of the page footer to give feedback.`}
              </span>
              <FeedbackForm
                isGeneralFeedback={false}
                onFeedbackSubmit={handleFeedbackSubmit}
                onRequestSuccess={handleRequestSuccess}
                onRequestError={handleRequestError}
                dataType={dataType}
              />
            </>
          ) : (
            <>
              <span id="widgetThankYouDesc" className="usa-sr-only">
                Your feedback helps us improve the TANF Data Portal. This
                message will close automatically.
              </span>
              <div className="feedback-widget-thank-you-header">
                <p
                  ref={thankYouHeadingRef}
                  id="feedbackThankYouWidgetHeader"
                  className="font-serif-xs margin-left-0 text-normal no-focus-outline"
                  tabIndex={-1}
                  aria-describedby="widgetThankYouDesc"
                >
                  Thank you for your feedback!
                </p>
                {showSpinner && (
                  <span
                    className="spinner margin-left-1"
                    aria-label="Loading"
                    aria-hidden={true}
                    role="status"
                  />
                )}
                <button
                  data-testid="feedback-widget-thank-you-close-button"
                  type="button"
                  className="usa-modal__close feedback-modal-close-button"
                  aria-label="Close feedback widget"
                  style={{
                    padding: '0',
                    alignSelf: 'center',
                    marginTop: '0',
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
            </>
          )}
        </div>
      </div>
    ) : null
  }
)

export default FeedbackWidget
