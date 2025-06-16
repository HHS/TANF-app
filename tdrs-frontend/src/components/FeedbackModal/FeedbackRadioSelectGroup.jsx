import React from 'react'
import classNames from 'classnames'
import '../../assets/feedback/Feedback.scss'

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
    icon: (
      <VeryBadIcon
        data-testid="icon-very-bad"
        title="Very Dissatisfied"
        role="svg"
      />
    ),
  },
  {
    label: 'Dissatisfied (2/5)',
    value: 2,
    color: 'orange',
    icon: <BadIcon data-testid="icon-bad" title="Dissatisfied" role="svg" />,
  },
  {
    label: 'Fair (3/5)',
    value: 3,
    color: 'blue',
    icon: <NeutralIcon data-testid="icon-fair" title="Fair" role="svg" />,
  },
  {
    label: 'Satisfied (4/5)',
    value: 4,
    color: 'green',
    icon: <GoodIcon data-testid="icon-good" title="Satisfied" role="svg" />,
  },
  {
    label: 'Very Satisfied (5/5)',
    value: 5,
    color: 'darkgreen',
    icon: (
      <VeryGoodIcon
        data-testid="icon-very-good"
        title="Very Satisfied"
        role="svg"
      />
    ),
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
      data-testid="feedback-ratings-select-group"
      className={classNames('feedback-group', 'usa-form-group', {
        error: error,
      })}
    >
      <fieldset className="usa-fieldset">
        <legend
          // @ts-ignore
          align="center"
          className={classNames(
            'usa-label',
            'font-serif-md',
            'feedback-label',
            {
              error: error,
            }
          )}
        >
          {label}
        </legend>
        <div className="rating-options">
          {feedbackRatingsList.map((option) => {
            const isSelected = selectedOption === option.value
            return (
              <div
                data-testid={`feedback-rating-option-${option.value}`}
                key={option.value}
                className={classNames(
                  'usa-radio',
                  'radio-option',
                  { selected: isSelected },
                  { [`selected-${option.color}`]: isSelected }
                )}
              >
                {option.icon && (
                  <label
                    key={option.value}
                    className="radio-icon"
                    style={{ color: option.color }}
                  >
                    <input
                      className="usa-radio__input"
                      data-testid={`feedback-radio-input-${option.value}`}
                      type="radio"
                      name={'tdpFeedbackRatings'}
                      value={option.value}
                      checked={isSelected}
                      onChange={() => onRatingSelected(option.value)}
                      tabIndex={0}
                    />
                    {option.icon}
                  </label>
                )}
              </div>
            )
          })}
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
