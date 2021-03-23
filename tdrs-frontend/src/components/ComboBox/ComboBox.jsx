import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

/**
 * @param {Component(s)} children - One or more React components to be rendered
 * as options in the STT combo box.
 * @param {function} handleSelect - A function to set the state of the STT
 * in EditProfile upon selection of an STT.
 * @param {string} selected - The name value of the STT. To be used as the
 * value of the select component.
 * @param {function} handleBlur - A function to run validation from
 * EditProfile on the Combo Box. Runs on blur of combo box element.
 * @param {string} error - If validation in EditProfile component throws
 * an error then it is passed to combo box to render the error information.
 * @param {string} name - A string used for the name and id values of
 * the combo box.
 * @param {string} placeholder - A string used as a placeholder
 * in the combo box.
 */
const ComboBox = ({
  children,
  handleSelect,
  selected,
  handleBlur,
  error,
  name,
  placeholder,
}) => {
  useEffect(() => {
    // The combo box was not rendering as a combo box without this line
    comboBox.init()

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
        Associated State, Tribe, or Territory
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
            handleBlur(e)
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
  handleBlur: PropTypes.func.isRequired,
  error: PropTypes.string,
  name: PropTypes.string.isRequired,
  placeholder: PropTypes.string,
}

ComboBox.defaultProps = {
  selected: '',
  error: '',
  placeholder: '',
}

export default ComboBox
