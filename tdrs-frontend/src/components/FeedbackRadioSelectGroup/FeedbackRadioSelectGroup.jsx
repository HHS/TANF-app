import React, { useState } from 'react'
import classNames from 'classnames'
import IconRadioSelect from '../IconRadioSelect/IconRadioSelect'

const FeedbackRadioSelectGroup = ({
  label,
  options,
  classes,
  onRatingSelected,
}) => {
  const [selectedValue, setSelectedValue] = useState('')

  const handleChange = (event) => {
    setSelectedValue(event.target.value)
  }

  return (
    <div className={classNames('usa-form-group', classes)}>
      <fieldset className="usa-fieldset">
        <legend className="usa-label text-bold">{label}</legend>
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
