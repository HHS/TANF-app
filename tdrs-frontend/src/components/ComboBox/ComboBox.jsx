import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({ children }) => {
  const selectRef = useRef()
  useEffect(() => {
    // The combo box was not rendering as a combo box without this line
    comboBox.init()
    // This solved the issue when tabbing through the form on EditProfile,
    // a selection was automatically being made on the first option
    selectRef.current.value = ''
  })
  return (
    <label className="usa-label" htmlFor="sttList">
      Associated State, Tribe, or Territory
      <div className="usa-combo-box" data-placeholder="- Select or Search -">
        <select className="usa-select" name="stt" id="stt" ref={selectRef}>
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
}

export default ComboBox
