import React, { useState } from 'react'
import classNames from 'classnames'
import IconRadioSelect from '../IconRadioSelect/IconRadioSelect'

const FeedbackRadioSelectGroup = ({
  label,
  options,
  classes,
  onRatingSelected,
  error,
  onError,
}) => {
  const [selectedValue, setSelectedValue] = useState('')

  const handleChange = (event) => {
    setSelectedValue(event.target.value)
    onRatingSelected(!selectedValue)
  }

  return (
    <div
      style={{ outline: '2px solid red' }}
      className={classNames('usa-form-group', classes)}
    >
      <fieldset className="usa-fieldset">
        <legend
          style={{
            color: error ? 'red' : 'black',
            backgroundColor: error ? 'lightcoral' : 'lightblue',
          }}
          className="usa-label text-bold"
        >
          {label}
        </legend>
        {options.map(({ option }, index) => (
          <IconRadioSelect
            label={option.label}
            value={option.value}
            icon={option.icon}
            checked={selectedValue === option.value}
            onChange={handleChange}
            classes={classes}
          />
        ))}
      </fieldset>
      <br />
      <h6 className="usa-h6">Pick a score and leave a comment</h6>
    </div>
  )
}

export default FeedbackRadioSelectGroup
