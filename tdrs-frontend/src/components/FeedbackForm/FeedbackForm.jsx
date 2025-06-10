/* eslint-disable no-unused-vars */
import React, { useEffect, useState } from 'react'
// @ts-ignore
import axios from 'axios'
import FeedbackRadioSelectGroup from '../FeedbackRadioSelectGroup/FeedbackRadioSelectGroup'

import { ReactComponent as VeryBadIcon } from '../../assets/feedback/very-dissatisfied-feedback.svg'
import { ReactComponent as BadIcon } from '../../assets/feedback/dissatisfied-feedback.svg'
import { ReactComponent as NeutralIcon } from '../../assets/feedback/neutral-feedback.svg'
import { ReactComponent as GoodIcon } from '../../assets/feedback/satisfied-feedback.svg'
import { ReactComponent as VeryGoodIcon } from '../../assets/feedback/very-satisfied-feedback.svg'

const feedbackRatingsList = [
  {
    label: 'Very Dissatisfied (1/5)',
    value: 1,
    color: 'red',
    icon: <VeryBadIcon />,
  },
  { label: 'Dissatisfied (2/5)', value: 2, color: 'orange', icon: <BadIcon /> },
  { label: 'Fair (3/5)', value: 3, color: 'blue', icon: <NeutralIcon /> },
  { label: 'Satisfied (4/5)', value: 4, color: 'green', icon: <GoodIcon /> },
  {
    label: 'Very Satisfied (5/5)',
    value: 5,
    color: 'darkgreen',
    icon: <VeryGoodIcon />,
  },
]

// @ts-ignore
const FeedbackForm = ({ onFeedbackSubmit }) => {
  // @ts-ignore
  const [canSubmit, setCanSubmit] = useState(false)
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [selectedRatingsOption, setSelectedRatingsOption] = useState()
  const [feedbackMessage, setFeedbackMessage] = useState('')
  const [error, setError] = useState(false)

  // Stubbed API call to submit feedback
  const handleSubmit = async () => {
    console.log('Attempting to submit user feedback...')
    if (isFormValidToSubmit()) {
      // TODO: add api subbing call in here
      onFeedbackSubmit() // Callback to parent component
    } else {
      setError(true)
      console.log('Please select a rating before submitting.')
    }
    //   try {
    //     const response = await axios.post('/api/feedback', { feedbackMessage })

    //     if (response.status === 200) {
    //       alert('Thank you for your feedback!')
    //       setFeedbackMessage('')
    //       onFeedbackSubmit() // Callback to parent component
    //     } else {
    //       alert('Something went wrong. Please try again.')
    //     }
    //   } catch (error) {
    //     console.error('Error submitting feedback:', error)
    //     alert('Failed to submit feedback.')
    //   }
    // } else {
    //   setError(true)
    //   alert('Please select a rating before submitting.')
    // }
  }

  const handleRatingSelected = (rating) => {
    setSelectedRatingsOption(rating)
  }

  const handleFeedbackMessageChange = (event) => {
    const message = event.target.value
    setFeedbackMessage(message)
  }

  const handleOnError = () => {
    setError(true)
  }

  const handleAnonymousChange = () => {
    console.log('Anonymous feedback:', !isAnonymous)
    setIsAnonymous(!isAnonymous)
  }

  const isFormValidToSubmit = () => {
    console.log(
      'Checking if form is valid to submit...' + selectedRatingsOption
    )
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
        <p style={{ color: error ? 'red' : 'none' }}>
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
              options={feedbackRatingsList}
              onRatingSelected={handleRatingSelected}
              error={error}
              onError={handleOnError}
            />
          </div>
          <div id="feedback-text-area" className="usa-form-group">
            <h3>Tell us more</h3>
            <textarea
              className="usa-textarea"
              value={feedbackMessage}
              onChange={handleFeedbackMessageChange}
              placeholder="Enter your feedback..."
              rows={9}
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
                  paddingTop: '0.25rem',
                }}
              >
                Send anonymously
              </label>
            </div>
          </div>
          <div className="margin-top-4 margin-bottom-2">
            <button
              id="feedback-submit-button"
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
