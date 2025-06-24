/* eslint-disable no-unused-vars */
import React, { useState } from 'react'
import axios from 'axios'
import Button from '../Button'
import FeedbackRadioSelectGroup from './FeedbackRadioSelectGroup'
import { feedbackPost } from '__mocks__/mockFeedbackAxiosApi'

const FeedbackForm = ({ onFeedbackSubmit }) => {
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
  const submitFeedbackForm = (data) => {
    return axios.post('/api/userFeedback/', data)
  }

  // Currently using stubbed API call to submit feedback
  // TODO: replace with above api call when implemented in backend (adjust url and data if needed)
  const handleSubmit = async () => {
    if (isFormValidToSubmit()) {
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
    } else {
      setError(true)
    }
  }

  const handleRatingSelected = (rating) => {
    setSelectedRatingsOption(rating)
    setError(false)
  }

  const handleFeedbackMessageChange = (event) => {
    const message = event.target.value.trimStart()
    setFeedbackMessage(message)
  }

  const handleAnonymousChange = () => {
    setIsAnonymous(!isAnonymous)
  }

  const handleKeyDown = (event, rating) => {
    if (event.key === 'Enter') {
      handleRatingSelected(rating)
    }
  }

  const isFormValidToSubmit = () => {
    return selectedRatingsOption !== undefined
  }

  return (
    <div>
      <div
        className="margin-4"
        style={{
          marginBottom: '4px',
        }}
      >
        <p
          data-testid="fields-required-text"
          style={{ color: error ? 'red' : 'black' }}
        >
          Fields marked with an asterisk (*) are required.
        </p>
      </div>
      {error && (
        <div className="usa-alert__body margin-4 margin-bottom-0 margin-top-0">
          <h3 className="usa-error-message">There is 1 error in this form</h3>
        </div>
      )}
      <form
        data-testid="feedback-form"
        style={{ marginTop: '1.5rem' }}
        onSubmit={(e) => {
          e.preventDefault()
          handleSubmit()
        }}
      >
        <div className="margin-4 margin-bottom-0" style={{ marginTop: '5px' }}>
          <div>
            <FeedbackRadioSelectGroup
              label="How is your overall experience using TANF Data Portal?*"
              selectedOption={selectedRatingsOption}
              onRatingSelected={handleRatingSelected}
              onKeyDownSelection={handleKeyDown}
              error={error}
            />
          </div>
          <div id="feedback-text-area" className="usa-form-group">
            <h3>Tell us more</h3>
            <textarea
              data-testid="feedback-message-input"
              className="usa-textarea feedback-textarea"
              value={feedbackMessage}
              onChange={handleFeedbackMessageChange}
              placeholder="Enter your feedback..."
              rows={10}
              cols={72}
              maxLength={500}
              style={{
                border: '2px solid black',
                marginTop: '-6px',
                maxWidth: '100%',
              }}
            />
            <div
              className="usa-character-count__message"
              style={{ marginTop: '2px' }}
            >
              {feedbackMessage.length}/{500} characters
            </div>
          </div>
          <div className="margin-top-3">
            <div className="usa-checkbox">
              <input
                id="feedback-anonymous-input"
                className="usa-checkbox__input"
                type="checkbox"
                checked={isAnonymous}
                onChange={handleAnonymousChange}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleAnonymousChange()
                  }
                }}
              />
              <label
                className="usa-checkbox__label"
                htmlFor="feedback-anonymous-input"
                style={{
                  display: 'inline-block',
                  paddingTop: '0.15rem',
                }}
              >
                Send anonymously
              </label>
            </div>
          </div>
          <div className="margin-top-4 margin-bottom-2">
            <Button
              data-testid="feedback-submit-button"
              type="submit"
              className="usa-button"
            >
              Send Feedback
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}

export default FeedbackForm
