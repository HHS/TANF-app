/* eslint-disable no-unused-vars */
import React, { useState } from 'react'
import axios from 'axios'
import FeedbackRadioSelectGroup from '../FeedbackRadioSelectGroup'
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

  const submitForm = (data) => {
    return axios.post('/api/userFeedback/', data)
  }

  // Currently using stubbed API call to submit feedback
  // TODO: replace with above api call when implement in backend (adjust url and data if needed)
  const handleSubmit = async () => {
    console.log('Attempting to send user feedback...')
    if (isFormValidToSubmit()) {
      try {
        // api stubbing (mock) call here
        const response = await feedbackPost('/api/userFeedback/', {
          rating: selectedRatingsOption,
          feedback: feedbackMessage,
          anonymous: isAnonymous,
        })

        if (response.status === 200) {
          onFeedbackSubmit()
          resetStatesOnceSubmitted() // Reset states after submission
          console.log('Feedback submitted successfully!')
        } else {
          console.log('Something went wrong. Please try again.')
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
      console.log('Please select a rating before submitting.')
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
      <form style={{ marginTop: '1.5rem' }} onSubmit={handleSubmit}>
        <div className="margin-4 margin-bottom-0" style={{ marginTop: '5px' }}>
          <div>
            <FeedbackRadioSelectGroup
              label="How is your overall experience using TANF Data Portal?*"
              selectedOption={selectedRatingsOption}
              onRatingSelected={handleRatingSelected}
              error={error}
            />
          </div>
          <div id="feedback-text-area" className="usa-form-group">
            <h3>Tell us more</h3>
            <textarea
              data-testid="feedback-message-input"
              className="usa-textarea"
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
              />
              <label
                className="usa-checkbox__label"
                htmlFor="feedback-anonymous-input"
                style={{
                  display: 'inline',
                  paddingTop: '0.15rem',
                }}
              >
                Send anonymously
              </label>
            </div>
          </div>
          <div className="margin-top-4 margin-bottom-2">
            <button
              data-testid="feedback-submit-button"
              type="button"
              className="usa-button"
              onClick={handleSubmit}
            >
              Send Feedback
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}

export default FeedbackForm
