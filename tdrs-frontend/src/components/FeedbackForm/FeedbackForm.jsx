import React, { useEffect, useState } from 'react'
import axios from 'axios'
import FeedbackRadioSelectGroup from '../FeedbackRadioSelectGroup/FeedbackRadioSelectGroup'

import { ReactComponent as VeryBadIcon } from '../../assets/feedback/very-dissatified-feedback.svg'
import { ReactComponent as BadIcon } from '../../assets/feedback/dissatisfied-feedback.svg'
import { ReactComponent as NeutralIcon } from '../../assets/feedback/fair-feedback.svg'
import { ReactComponent as GoodIcon } from '../../assets/feedback/satisfied-feedback.svg'
import { ReactComponent as VeryGoodIcon } from '../../assets/feedback/very-satisfied-feedback.svg'

const feedbackRatingsList = [
  { label: 'Very Satisfied (5/5)', value: 5, icon: <VeryGoodIcon /> },
  { label: 'Satisfied (4/5)', value: 4, icon: <GoodIcon /> },
  { label: 'Fair (3/5)', value: 3, icon: <NeutralIcon /> },
  { label: 'Dissatisfied (2/5)', value: 2, icon: <BadIcon /> },
  { label: 'Very Dissatisfied (1/5)', value: 1, icon: <VeryBadIcon /> },
]

const FeedbackForm = ({ onFeedbackSubmit }) => {
  const [user, setUser] = useState(null)
  const [canSubmit, setCanSubmit] = useState(false)
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [selectedRatingsOption, setSelectedRatingsOption] = useState()
  const [feedbackMessage, setFeedbackMessage] = useState('')
  const [error, setError] = useState(false)

  // Stubbed API call to submit feedback
  const handleSubmit = async () => {
    if (isFormValidToSubmit) {
      try {
        const response = await axios.post('/api/feedback', { feedbackMessage })

        if (response.status === 200) {
          alert('Thank you for your feedback!')
          setFeedbackMessage('')
          onFeedbackSubmit() // Callback to parent component
        } else {
          alert('Something went wrong. Please try again.')
        }
      } catch (error) {
        console.error('Error submitting feedback:', error)
        alert('Failed to submit feedback.')
      }
    } else {
      setError(true)
      alert('Please select a rating before submitting.')
    }
    
  }

  // Stubbed API call to fetch user data
  // Fetch user data when the component mounts
  const getUser = async () => {
    try {
      const response = await axios.get('/api/user')
      if (response.status === 200) {
        setUser(response.data)
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
    }
  }

  const handleRatingSelected = (rating) => {
    setSelectedRatingsOption(rating)
  }

  const handleFeedbackMessageChange = (event) => {
    const message = event.target.value
    setFeedbackMessage(message)
  }

  const isFormValidToSubmit = () => {
    return selectedRatingsOption !== undefined
  }

  useEffect(() => {
    getUser()
  }, [])

  return (
    <div>
      {error && (
        <div className="usa-alert usa-alert--error">
          <div className="usa-alert__body">
            <h3 style={{ color: 'red' }}className="usa-alert__heading">There is 1 error in this form</h3>
          </div>
        </div>
      )}
      <div style={{ marginTop: '10px' }}>
        <FeedbackRadioSelectGroup
          label="How is your overall experience using TANF Data Portal?*"
          options={feedbackRatingsList}
          classes="feedback-radio-select-group"
          onRatingSelected={handleRatingSelected}
          error={error}
          onError=
        />
        <br />
        <div id="feedback-text-area" className="usa-form-group">
          <h5>Tell us more</h5>
          <br />
          <textarea
            value={feedbackMessage}
            onChange={handleFeedbackMessageChange}
            placeholder="Enter your feedback..."
            rows={5}
            cols={50}
            maxLength={500}
          />
          <div>
            {feedbackMessage.length}/{500} characters
          </div>
        </div>
        <br />
        <div className="margin-top-2">
          <label className="usa-radio__label">
            <div className="usa-radio">
              <input
                className="usa-radio__input"
                id="feedback-anonymous-input"
                type="checkbox"
                name="feedback-anonymous"
                checked={isAnonymous}
                onChange={() => setIsAnonymous(!isAnonymous)}
              />
            </div>
            Send anonymously
          </label>
        </div>
        <br />
        <div className="margin-x-4 margin-bottom-4">
          <button
            id="feedback-submit-button"
            type="button"
            className="mobile:margin-bottom-1 mobile-lg:margin-bottom-0"
            onClick={handleSubmit}
          >
            Send Feedback
          </button>
        </div>
      </div>
    </div>
  )
}

export default FeedbackForm
