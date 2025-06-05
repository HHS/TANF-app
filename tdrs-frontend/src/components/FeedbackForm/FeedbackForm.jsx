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
  const [shouldSubmit, setShouldSubmit] = useState(false)
  const [isAnonymous, setIsAnonymous] = useState(false)
  const [selectedRatingsOption, setSelectedRatingsOption] = useState()
  const [feedback, setFeedback] = useState('')

  // Stubbed API call to submit feedback
  const handleSubmit = async () => {
    try {
      const response = await axios.post('/api/feedback', { feedback })

      if (response.status === 200) {
        alert('Thank you for your feedback!')
        setFeedback('')
        onFeedbackSubmit() // Callback to parent component
      } else {
        alert('Something went wrong. Please try again.')
      }
    } catch (error) {
      console.error('Error submitting feedback:', error)
      alert('Failed to submit feedback.')
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

  useEffect(() => {
    getUser()
  }, [])

  return (
    <div>
      <div style={{ marginTop: '10px' }}>
        <FeedbackRadioSelectGroup
          label="How is your overall experience using TANF Data Portal?*"
          options={feedbackRatingsList}
          selectedRating={selectedRating}
          classes="feedback-radio-select-group"
        />
        <br />
        <h5>Tell us more</h5>
        <br />
        <textarea
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
          placeholder="Enter your feedback"
          rows="4"
          cols="40"
        />
        <br />
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
        <br />
        <button onClick={handleSubmit}>Send Feedback</button>
      </div>
    </div>
  )
}

export default FeedbackForm
