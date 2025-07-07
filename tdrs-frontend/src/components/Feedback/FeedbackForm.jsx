/* eslint-disable no-unused-vars */
import React, { useCallback, useEffect, useRef, useState } from 'react'
import axios from 'axios'
import axiosInstance from '../../axios-instance'
import classNames from 'classnames'
import FeedbackRadioSelectGroup from './FeedbackRadioSelectGroup'
import { feedbackPost } from '../../__mocks__/mockFeedbackAxiosApi'
import { useSelector } from 'react-redux'
import {
  FAIR_FEEDBACK,
  GOOD_FEEDBACK,
  GREAT_FEEDBACK,
  POOR_AND_BAD_FEEDBACK,
} from './FeedbackConstants'

const ratingMessageMap = {
  1: POOR_AND_BAD_FEEDBACK,
  2: POOR_AND_BAD_FEEDBACK,
  3: FAIR_FEEDBACK,
  4: GOOD_FEEDBACK,
  5: GREAT_FEEDBACK,
}

const FeedbackForm = ({ isGeneralFeedback, onFeedbackSubmit }) => {
  const formRef = useRef(null)
  const authenticated = useSelector((state) => state.auth.authenticated)

  const [isAnonymous, setIsAnonymous] = useState(false)
  const [selectedRatingsOption, setSelectedRatingsOption] = useState(undefined)
  const [feedbackMessage, setFeedbackMessage] = useState('')
  const [error, setError] = useState(false)

  const resetStatesOnceSubmitted = () => {
    setSelectedRatingsOption(undefined)
    setFeedbackMessage('')
    setError(false)
    setIsAnonymous(false)
  }

  // TODO: NOTE: make sure to use axiosInstance (to carry over auth creds) for the real api POST call
  const submitFeedbackForm = async (data) => {
    return axiosInstance.post('/api/userFeedback/', {
      rating: selectedRatingsOption,
      feedback: feedbackMessage,
      anonymous: isAnonymous,
    })
  }

  // Currently using stubbed API call to submit feedback
  // TODO: replace with above api call when implemented in backend (adjust url and data if needed)
  const handleSubmit = useCallback(async () => {
    if (!selectedRatingsOption) {
      setError(true)
      return
    }

    //if (isFormValidToSubmit()) {
    try {
      // api stubbing (mock) call here replace
      const response = await feedbackPost('/api/userFeedback/', {
        rating: selectedRatingsOption,
        feedback: feedbackMessage,
        anonymous: isAnonymous,
      })

      if (response.status === 200) {
        onFeedbackSubmit()
        resetStatesOnceSubmitted()
      } else {
        console.error('Something went wrong. Please try again.')
      }
    } catch (error) {
      if (error.response && error.response.status === 400) {
        console.error('Error submitting feedback:', error)
      } else {
        console.error('An unexpected error occurred. Please try again later.')
      }
    }
    // } else {
    //   setError(true)
    // }
  }, [selectedRatingsOption, feedbackMessage, isAnonymous, onFeedbackSubmit])

  const handleRatingSelected = (rating) => {
    setSelectedRatingsOption(rating)
    setError(false)
  }

  const handleFeedbackMessageChange = (event) => {
    const message = event.target.value.trimStart()
    setFeedbackMessage(message)
  }

  const handleAnonymousChange = () => setIsAnonymous((prev) => !prev)

  const handleRadioKeyDown = (event, rating) => {
    if (event.key === 'Enter') {
      handleRatingSelected(rating)
    }
  }

  //const isFormValidToSubmit = () => selectedRatingsOption !== undefined

  useEffect(() => {
    if (!isGeneralFeedback) return // Only add listener when modal is open

    const handleKeyDown = (e) => {
      const isCmdOrCtrl = e.metaKey || e.ctrlKey
      const isEnter = e.key === 'Enter'

      if (isCmdOrCtrl && isEnter) {
        const isInsideForm = formRef.current?.contains(document.activeElement)
        if (isInsideForm) {
          e.preventDefault()
          handleSubmit()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleSubmit, isGeneralFeedback])

  function renderAnonymousCheckbox({ isAnonymous, handleAnonymousChange }) {
    return (
      <div
        className={
          isGeneralFeedback ? 'margin-left-4 margin-top-1' : 'margin-bottom-1'
        }
      >
        <div
          className="usa-checkbox"
          style={{ marginLeft: !isGeneralFeedback ? '12px' : '' }}
        >
          <input
            id="feedback-anonymous-input"
            className="usa-checkbox__input"
            type="checkbox"
            checked={isAnonymous}
            onChange={handleAnonymousChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleAnonymousChange()
              }
            }}
          />
          <label
            className="usa-checkbox__label"
            htmlFor="feedback-anonymous-input"
            style={{
              display: isGeneralFeedback ? 'inline-block' : '',
            }}
          >
            Send anonymously
          </label>
        </div>
      </div>
    )
  }

  return (
    <form
      ref={formRef}
      data-testid="feedback-form"
      style={{ marginTop: isGeneralFeedback ? '1.5rem' : '0.5rem' }}
      onSubmit={(e) => {
        e.preventDefault()
      }}
    >
      {isGeneralFeedback && (
        <>
          <div
            className="margin-4"
            style={{
              marginBottom: '4px',
            }}
          >
            <p
              data-testid="fields-required-text"
              style={{ color: error ? '#b50909' : '#575c64' }}
            >
              Fields marked with an asterisk (*) are required.
            </p>
          </div>
          {error && (
            <div
              role="alert"
              className="usa-alert__body margin-4 margin-bottom-0 margin-top-0"
            >
              <h3 className="usa-error-message">
                There is 1 error in this form
              </h3>
            </div>
          )}
        </>
      )}
      {!isGeneralFeedback &&
        renderAnonymousCheckbox({
          isAnonymous,
          handleAnonymousChange,
        })}
      <div
        className={classNames('margin-bottom-0', {
          'margin-4': isGeneralFeedback,
        })}
        style={{
          marginTop: isGeneralFeedback ? '4px' : '',
        }}
      >
        <FeedbackRadioSelectGroup
          label="How is your overall experience using TANF Data Portal?*"
          selectedOption={selectedRatingsOption}
          onRatingSelected={handleRatingSelected}
          onKeyDownSelection={handleRadioKeyDown}
          showLabel={isGeneralFeedback ? true : false}
          isModal={isGeneralFeedback ? true : false}
          error={error}
        />
      </div>
      {(isGeneralFeedback || selectedRatingsOption) && (
        <div
          id="feedback-text-area"
          className={isGeneralFeedback ? 'usa-form-group margin-4' : ''}
        >
          {isGeneralFeedback ? (
            <h3>Tell us more</h3>
          ) : (
            selectedRatingsOption && (
              <p
                className="margin-bottom-2"
                style={{
                  fontWeight: 'bold',
                  fontSize: '0.90rem',
                }}
              >
                {ratingMessageMap[selectedRatingsOption]}
              </p>
            )
          )}
          <textarea
            data-testid="feedback-message-input"
            className="usa-textarea feedback-textarea"
            value={feedbackMessage}
            onChange={handleFeedbackMessageChange}
            placeholder="Enter your feedback..."
            rows={isGeneralFeedback ? 10 : 4}
            cols={isGeneralFeedback ? 72 : 30}
            maxLength={500}
            style={{
              border: '1px solid black',
              marginTop: '-6px',
              maxWidth: '100%',
              fontSize: isGeneralFeedback ? '1rem' : '0.85rem',
              padding: isGeneralFeedback ? '0.75rem' : '0.4rem',
            }}
          />
          {isGeneralFeedback && (
            <div
              className="usa-character-count__message"
              style={{ marginTop: '2px' }}
            >
              {feedbackMessage.length}/{500} characters
            </div>
          )}
        </div>
      )}
      {authenticated &&
        isGeneralFeedback &&
        renderAnonymousCheckbox({
          isAnonymous,
          handleAnonymousChange,
        })}
      {(isGeneralFeedback || selectedRatingsOption) && (
        <div
          className={classNames({
            'margin-top-4': isGeneralFeedback,
            'margin-top-2': !isGeneralFeedback,
            'margin-bottom-2': isGeneralFeedback,
            'margin-left-4': isGeneralFeedback,
          })}
        >
          <button
            data-testid="feedback-submit-button"
            type="button"
            className="usa-button"
            onClick={handleSubmit}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                handleSubmit()
              }
            }}
          >
            Send Feedback
          </button>
        </div>
      )}
    </form>
  )
}

export default FeedbackForm
