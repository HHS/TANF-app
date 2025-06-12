import React, { useState } from 'react'

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
    icon: <VeryBadIcon data-testid="icon-very-bad" title="Very Dissatisfied" />,
  },
  {
    label: 'Dissatisfied (2/5)',
    value: 2,
    color: 'orange',
    icon: <BadIcon data-testid="icon-bad" title="Dissatisfied" />,
  },
  {
    label: 'Fair (3/5)',
    value: 3,
    color: 'blue',
    icon: <NeutralIcon data-testid="icon-fair" title="Fair" />,
  },
  {
    label: 'Satisfied (4/5)',
    value: 4,
    color: 'green',
    icon: <GoodIcon data-testid="icon-good" title="Satisfied" />,
  },
  {
    label: 'Very Satisfied (5/5)',
    value: 5,
    color: 'darkgreen',
    icon: <VeryGoodIcon data-testid="icon-very-good" title="Very Satisfied" />,
  },
]

const FeedbackRadioSelectGroup = ({
  label,
  selectedOption,
  onRatingSelected,
  error,
}) => {
  return (
    <div
      style={{
        outline: error ? '2px solid #b50909' : '2px solid #e2eff7',
        justifyContent: 'center',
        alignItems: 'center',
        width: '37.5rem',
        height: '9.375rem',
        backgroundColor: error ? '#f4e3db' : '#e2eff7',
        textAlign: 'center',
        borderRadius: '0.5rem',
      }}
      data-testid="feedback-ratings-select-group"
      className="usa-form-group"
    >
      <fieldset className="usa-fieldset">
        <legend
          // @ts-ignore
          align="center"
          style={{
            color: error ? '#b50909' : 'black',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            paddingTop: '25px',
          }}
          className="usa-label font-serif-md"
        >
          {label}
        </legend>
        <div
          style={{
            display: 'flex',
            flexDirection: 'row',
            justifyContent: 'center',
            alignItems: 'center',
            marginTop: '10px',
          }}
        >
          {feedbackRatingsList.map((option) => (
            <div
              data-testid={`feedback-rating-option-${option.value}`}
              key={option.value}
              className="usa-radio"
              style={{
                border:
                  selectedOption === option.value
                    ? `1px solid ${option.value}`
                    : '1px solid black',
              }}
            >
              {option.icon && (
                <label
                  style={{
                    cursor: 'pointer',
                    zIndex: '2',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: option.color,
                    padding: '4px',
                    width: '45px',
                    border:
                      selectedOption !== undefined &&
                      selectedOption === option.value
                        ? `2px solid ${option.color}`
                        : 'none',
                  }}
                  key={option.value}
                  className="radio-icon"
                >
                  <input
                    className="usa-radio__input"
                    data-testid={`usa-radio-input-${option.value}`}
                    type="radio"
                    name={'tdpFeedbackRatings'}
                    value={option.value}
                    checked={selectedOption === option.value}
                    onChange={() => onRatingSelected(option.value)}
                  />
                  {option.icon}
                </label>
              )}
            </div>
          ))}
        </div>
      </fieldset>
      <div
        style={{
          display: 'block',
          paddingTop: '0px',
        }}
      >
        <p className="margin-top-1">Pick a score and leave a comment</p>
      </div>
    </div>
  )
}

export default FeedbackRadioSelectGroup
