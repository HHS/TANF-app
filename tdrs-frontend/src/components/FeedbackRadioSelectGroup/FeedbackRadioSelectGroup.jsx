import React, { useState } from 'react'
import IconRadioSelect from '../IconRadioSelect/IconRadioSelect'

const FeedbackRadioSelectGroup = ({
  label,
  options,
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
          {options.map((option) => (
            <IconRadioSelect
              key={`radio-${option.value}`}
              label={option.label}
              value={option.value}
              icon={option.icon}
              checked={selectedValue === option.value}
              onChange={handleChange}
              color={option.color}
            />
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
