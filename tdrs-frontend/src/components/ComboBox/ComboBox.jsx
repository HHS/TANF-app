import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

/**
 * @param {ReactNode} children - One or more React components to be rendered
 * as options in the combo box.
 * @param {function} handleSelect - A function to set the state
 * of the selected option.
 * @param {string} selected - The value of the selected option.
 * @param {function} handleBlur - Runs on blur of combo box element.
 * @param {string} error - If validation in EditProfile component throws
 * an error then it is passed to combo box to render the error information.
 * @param {string} name - A string used for the name and id values of
 * the combo box.
 * @param {string} placeholder - A string used as a placeholder
 * in the combo box.
 * @param {string} label - The text content for the label tied to
 * the combo box.
 */
const ComboBox = ({
  children,
  handleSelect,
  selected,
  handleBlur,
  error,
  name,
  placeholder,
  label,
}) => {
  useEffect(() => {
    // The combo box was not rendering as a combo box without this line
    comboBox.init()
  }, [])

  useEffect(() => {
    const input = document.querySelector('.usa-combo-box__input')
    if (input) {
      if (error) {
        input.classList.add('usa-combo-box__input--error')
      }

      if (!error) {
        input.classList.remove('usa-combo-box__input--error')
      }
    }
  })

  return (
    <>
      {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
      <label
        className={`usa-label text-bold ${error ? 'usa-label--error' : ''}`}
        htmlFor={name}
      >
        {label}
      </label>
      {error && (
        <span className="usa-error-message" id={`${name}-error-message`}>
          {error}
        </span>
      )}
      <div className="usa-combo-box" data-placeholder={placeholder}>
        {/* eslint-disable-next-line jsx-a11y/no-onchange */}
        <select
          className="usa-select"
          data-testid={`${name}-combobox`}
          name={name}
          id={name}
          onChange={(e) => {
            handleSelect(e.target.value)
            handleBlur && handleBlur(e)
          }}
          value={selected}
        >
          {children}
        </select>
      </div>
    </>
  )
}

ComboBox.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired,
  handleSelect: PropTypes.func.isRequired,
  selected: PropTypes.string,
  handleBlur: PropTypes.func,
  error: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
  label: PropTypes.string.isRequired,
}

ComboBox.defaultProps = {
  selected: '',
  error: '',
  placeholder: '',
  handleBlur: null,
}

export default ComboBox
