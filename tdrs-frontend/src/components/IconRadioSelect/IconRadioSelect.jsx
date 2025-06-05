import React from 'react'
import classNames from 'classnames'
import Tooltip from '../Tooltip/Tooltip'

const IconRadioSelect = ({
  label,
  value,
  icon,
  checked,
  onChange,
  classes,
}) => {
  // TODO: need to wrap radio buttons in a tooltip
  return (
    <Tooltip text={label}>
      <div className="usa-radio">
        <input
          className="usa-radio__input"
          id={`usa-radio__input-${value}`}
          type="radio"
          name={`tdpFeedbackRating-${value}`}
          value={value}
          checked={checked}
          onChange={onChange}
        />
        <label
          aria-label={label}
          className={classNames('usa-radio__label', classes)}
          htmlFor={value}
        >
          {icon && (
            <span
              style={{ zIndex: '2', display: 'flex', alignItems: 'center' }}
              className="radio-icon"
            >
              {icon}
            </span>
          )}
        </label>
      </div>
    </Tooltip>
  )
}

export default IconRadioSelect
