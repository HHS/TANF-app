import React from 'react'

const IconRadioSelect = ({ label, value, icon, checked, onChange, color }) => {
  // TODO: may want to add a tooltip for icon selects for users
  return (
    <div className="usa-radio" style={{ border: '1px solid black' }}>
      <input
        className="usa-radio__input"
        id={`usa-radio-input-${value}`}
        type="button"
        name={`tdpFeedbackRating-${value}`}
        value={value}
        checked={checked}
        onChange={onChange}
      />
      {icon && (
        <span
          style={{
            cursor: 'pointer',
            zIndex: '2',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color,
            padding: '4px',
            width: '45px',
            border: checked ? `1px solid ${color}` : 'none',
          }}
          className="radio-icon"
        >
          {icon}
        </span>
      )}
    </div>
  )
}

export default IconRadioSelect
