/* eslint-disable no-unused-vars */
import React, { useCallback, useEffect, useRef, useState } from 'react'
import axiosInstance from '../../axios-instance'
import classNames from 'classnames'
import FeedbackRadioSelectGroup from './FeedbackRadioSelectGroup'
import { useSelector } from 'react-redux'
import {
  FAIR_FEEDBACK,
  GOOD_FEEDBACK,
  GREAT_FEEDBACK,
  POOR_AND_BAD_FEEDBACK,
  GENERAL_FEEDBACK_TYPE,
} from './FeedbackConstants'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL

const ratingMessageMap = {
  1: POOR_AND_BAD_FEEDBACK,
  2: POOR_AND_BAD_FEEDBACK,
  3: FAIR_FEEDBACK,
  4: GOOD_FEEDBACK,
  5: GREAT_FEEDBACK,
}

const FeedbackForm = ({
  isGeneralFeedback,
  onFeedbackSubmit,
  onRequestSuccess,
  onRequestError,
  dataType = null,
}) => {
  const formRef = useRef(null)
  const authenticated = useSelector((state) => state.auth.authenticated)
  const { widgetId, dataFiles } = useSelector((state) => state.feedbackWidget)

  const [isAnonymous, setIsAnonymous] = useState(false)
  const [selectedRatingsOption, setSelectedRatingsOption] = useState(undefined)
  const [feedbackMessage, setFeedbackMessage] = useState('')
  const [hasError, setHasError] = useState(false)
  const [feedbackID, setFeedbackID] = useState(null)

  // Determine values based on props and state
  const isGeneral = isGeneralFeedback

  const resetStatesOnceSubmitted = () => {
    setSelectedRatingsOption(undefined)
    setFeedbackMessage('')
    setHasError(false)
    setIsAnonymous(false)
  }

  const postFeedback = useCallback(async (payload) => {
    return axiosInstance.post(`${BACKEND_URL}/feedback/`, payload, {
      headers: { 'Content-Type': 'application/json' },
      withCredentials: true,
    })
  }, [])

  const updateFeedback = useCallback(
    async (payload) => {
      return axiosInstance.patch(
        `${BACKEND_URL}/feedback/${feedbackID}/`,
        payload,
        {
          headers: { 'Content-Type': 'application/json' },
          withCredentials: true,
        }
      )
    },
    [feedbackID]
  )

  const handlePayloadAttachments = (payload, isGeneral) => {
    let updatedPayload = { ...payload }
    if (!isGeneral) {
      // Only include widget_id and data files for non-general feedback
      updatedPayload.widget_id = widgetId || 'unknown-submission-feedback'

      // include data files
      if (Array.isArray(dataFiles)) {
        updatedPayload.attachments = dataFiles.map((file) => ({
          content_type: 'datafile',
          object_id: file.id,
        }))
      } else if (dataFiles) {
        console.log('Datafile: ', JSON.stringify(dataFiles, null, 2))
        updatedPayload.attachments = [
          { content_type: 'datafile', object_id: dataFiles.file.id },
        ]
      } else {
        updatedPayload.attachments = []
      }
    }
    return updatedPayload
  }

  const constructPayload = () => {
    // Set feedback_type
    const feedbackType = isGeneral ? GENERAL_FEEDBACK_TYPE : dataType

    // TODO: still need to figure out how to get component info or some context for component value
    // Set component -------------------------
    const component = isGeneral ? 'general-website' : 'data-file-submission'
    // ------------------------------------------------------

    // Setup payload
    let payload = {
      rating: selectedRatingsOption,
      feedback: feedbackMessage,
      anonymous: isAnonymous,
      page_url: window.location.href,
      feedback_type: feedbackType,
      component: component,
    }

    payload = handlePayloadAttachments(payload, isGeneral)
    return payload
  }

  const submitFeedback = useCallback(
    async (payload) => {
      try {
        const response = feedbackID
          ? await updateFeedback(payload)
          : await postFeedback(payload)

        if (response.status === 200 || response.status === 201) {
          setFeedbackID(response.data.id)
        }
        return response
      } catch (error) {
        console.error('Error submitting feedback:', error)
        onRequestError?.()
      }
    },
    [
      feedbackID,
      isGeneral,
      isAnonymous,
      widgetId,
      dataFiles,
      dataType,
      handlePayloadAttachments,
      updateFeedback,
      postFeedback,
    ]
  )

  const handleSubmit = useCallback(async () => {
    if (!selectedRatingsOption) {
      setHasError(true)
      return
    }

    try {
      const payload = constructPayload()
      const response = await submitFeedback(payload)

      if (response.status === 200 || response.status === 201) {
        onFeedbackSubmit()
        onRequestSuccess?.()
        resetStatesOnceSubmitted()
      } else {
        console.error('Unexpected response: ', response)
        onRequestError?.()
      }
    } catch (error) {
      const status = error?.response?.status
      if (status === 400) {
        console.error('Error submitting feedback: ', error.response)
      } else {
        console.error(
          'An unexpected error occurred. Please try again later.',
          error
        )
      }
      onRequestError?.()
    }
  }, [
    selectedRatingsOption,
    isGeneral,
    feedbackMessage,
    isAnonymous,
    widgetId,
    dataFiles,
    onFeedbackSubmit,
    onRequestSuccess,
    onRequestError,
    submitFeedback,
  ])

  const handleRatingSelected = async (rating) => {
    setSelectedRatingsOption(rating)
    const payload = { ...constructPayload(), rating: rating }
    await submitFeedback(payload)
    setHasError(false)
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
          isGeneralFeedback ? 'margin-left-4 margin-top-1' : 'margin-bottom-0'
        }
      >
        <div
          className={classNames('usa-checkbox', {
            'margin-left-2': !isGeneralFeedback,
          })}
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
            className={`usa-checkbox__label ${!isGeneralFeedback ? 'feedback-widget-anonymous-label' : ''}`}
            htmlFor="feedback-anonymous-input"
            style={{
              display: isGeneralFeedback ? 'inline-block' : '',
              color: !isGeneralFeedback ? '#575c64' : '',
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
      style={{ marginTop: isGeneralFeedback ? '1.5rem' : '' }}
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
              style={{ color: hasError ? '#b50909' : 'black' }}
            >
              Fields marked with an asterisk (*) are required.
            </p>
          </div>
          {hasError && (
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
          showLabel={isGeneralFeedback}
          isModal={isGeneralFeedback}
          error={hasError}
        />
      </div>
      {(isGeneralFeedback || selectedRatingsOption) && (
        <div
          id="feedback-text-area"
          className={isGeneralFeedback ? 'usa-form-group margin-4' : ''}
          style={{ boxSizing: !isGeneralFeedback ? 'border-box' : '' }}
        >
          {isGeneralFeedback ? (
            <h3>Tell us more</h3>
          ) : (
            selectedRatingsOption && (
              <div
                aria-live="polite"
                aria-atomic="true"
                className="margin-left-1 margin-bottom-1 margin-top-1"
                style={{
                  fontSize: '0.90rem',
                  color: '#575c64',
                  minHeight: '1.2em', // helps avoid layout shift
                }}
              >
                <p>{ratingMessageMap[selectedRatingsOption]}</p>
              </div>
            )
          )}
          <textarea
            data-testid="feedback-message-input"
            className={classNames(
              `usa-textarea ${!isGeneralFeedback ? 'feedback-widget-textarea' : ''}`
            )}
            value={feedbackMessage}
            onChange={handleFeedbackMessageChange}
            placeholder="Enter your feedback..."
            rows={isGeneralFeedback ? 10 : 4}
            cols={isGeneralFeedback ? 72 : 30}
            maxLength={500}
            style={{
              border: '1px solid black',
              marginTop: '-4px',
              maxWidth: '100%',
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
          className={classNames('margin-bottom-2', {
            'margin-top-4': isGeneralFeedback,
            'margin-top-2': !isGeneralFeedback,
            'margin-left-4': isGeneralFeedback,
            'margin-left-1': !isGeneralFeedback,
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
