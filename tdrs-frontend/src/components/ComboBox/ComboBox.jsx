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
    const selectEl = document.querySelector('.usa-select')

    const selectElChange = (e) => {
      console.log('triggered on select', e)
      handleBlur(e)
      handleSelect(e.detail.value)
    }

    const clearButtonClick = () => {
      handleSelect('')
      selectEl.value = ''
    }

    const testFunction = (e) => {
      console.log('triggered on click', e)
    }

    if (selectEl) {
      console.log('why tho?')
      selectEl.addEventListener('change', selectElChange)
      selectEl.addEventListener('click', testFunction)
    }

    const clearButton = document.querySelector('.usa-combo-box__clear-input')
    if (clearButton) {
      clearButton.addEventListener('click', clearButtonClick)
    }

    // The combo box was not rendering as a combo box without this line
    comboBox.init()
    // This solved the issue when tabbing through the form on EditProfile,
    // a selection was automatically being made on the first option
    selectEl.value = ''

    const input = document.querySelector('.usa-combo-box__input')

    if (input) {
      if (error) {
        input.classList.add('usa-combo-box__input--error')
      }

      if (!error) {
        input.classList.remove('usa-combo-box__input--error')
      }
    }

    return () => {
      selectEl.removeEventListener('change', selectElChange)
      if (clearButton) {
        clearButton.removeEventListener('click', clearButtonClick)
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
          onChange={() => {}}
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
