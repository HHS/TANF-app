import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({ children, handleSelect, selected, handleBlur, error }) => {
  const selectRef = useRef()
  useEffect(() => {
    // The combo box was not rendering as a combo box without this line
    comboBox.init()
    // This solved the issue when tabbing through the form on EditProfile,
    // a selection was automatically being made on the first option
    selectRef.current.value = ''

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
    <div className="usa-combo-box">
      {/* eslint-disable-next-line */}
      <select
        className="usa-select"
        name="stt"
        id="stt"
        ref={selectRef}
        onChange={(e) => {
          handleBlur(e)
          handleSelect(e.target.value)
        }}
        value={selected}
      >
        {children}
      </select>
    </div>
  )
}

ComboBox.propTypes = {
  children: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      id: PropTypes.number,
    })
  ).isRequired,
  handleSelect: PropTypes.func.isRequired,
  selected: PropTypes.string,
  handleBlur: PropTypes.func.isRequired,
  error: PropTypes.string,
}

ComboBox.defaultProps = {
  selected: '',
  error: '',
}

export default ComboBox
