import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({
  children,
  handleSelect,
  selected,
  handleBlur,
  error,
  name,
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
    <label className="usa-label" htmlFor={name.toUpperCase()}>
      Associated State, Tribe, or Territory
      {error && (
        <span
          className="usa-error-message"
          id="input-error-message"
          role="alert"
        >
          {error}
        </span>
      )}
      <div className="usa-combo-box">
        {/* eslint-disable-next-line */}
        <select
          className="usa-select"
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
    </label>
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
}

ComboBox.defaultProps = {
  selected: '',
  error: '',
}

export default ComboBox
