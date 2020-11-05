import React from 'react'
import PropTypes from 'prop-types'

function FormGroup({
  error,
  label,
  name,
  inputValue,
  handleChange,
  handleBlur,
}) {
  return (
    <div className={`usa-form-group ${error ? 'usa-form-group--error' : ''}`}>
      <label
        className={`usa-label ${error ? 'usa-label--error' : ''}`}
        htmlFor={name}
      >
        {label} (required)
        {error && (
          <span
            className="usa-error-message"
            id={`${name}-error-message`}
            role="alert"
          >
            {error}
          </span>
        )}
        <input
          className={`usa-input ${error ? 'usa-input--error' : ''}`}
          id={name}
          name={name}
          type="text"
          aria-required="true"
          value={inputValue}
          onChange={({ target: { value } }) => {
            handleChange({ name, value })
          }}
          onBlur={handleBlur}
        />
      </label>
    </div>
  )
}

FormGroup.propTypes = {
  error: PropTypes.string,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  inputValue: PropTypes.string,
  handleChange: PropTypes.func.isRequired,
  handleBlur: PropTypes.func.isRequired,
}

FormGroup.defaultProps = {
  error: '',
  inputValue: '',
}

export default FormGroup
