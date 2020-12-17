import React from 'react'
import PropTypes from 'prop-types'

/**
 * FormGroup renders a group of elements for a form.
 * This includes a form group, label, error span, and an input.
 * The span will only be rendered if there is an error, and some
 * classes will be added to match USWDS form styling.
 * @param {string} error - if there is an error from an input being empty,
 * it will be passed here.
 * @param {string} label - this will be the string value used for the label
 * of the input and is required.
 * @param {string} name - this string will be used for the id's and class
 * names of the input to ensure that they are unique and is required.
 * @param {string} inputValue - this value is used to make the input a
 * controlled component.
 * @param {function} handleChange - this is a function to update the state
 * with the value of the input.
 * @param {function} handleBlur - this is a function that is passed in
 * to handle the blur event of the input.
 */
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
        className={`usa-label text-bold ${error ? 'usa-label--error' : ''}`}
        htmlFor={name}
      >
        {label} (required)
        {error && (
          <span className="usa-error-message" id={`${name}-error-message`}>
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
