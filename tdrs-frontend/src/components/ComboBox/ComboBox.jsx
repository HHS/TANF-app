import React, { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({ sttList }) => {
  const comboBoxRef = useRef()
  let select
  useEffect(() => {
    comboBox.init()
    if (comboBoxRef.current) {
      comboBox.on(comboBoxRef.current)
    }
    select = document.querySelector('.usa-select')
    console.log('SELECT', select.value)
  }, [comboBoxRef])

  return (
    <label className="usa-label" htmlFor="stt">
      Associated State, Tribe, or Territory
      <div className="usa-combo-box" ref={comboBoxRef}>
        <select className="usa-select" name="stt" id="stt">
          {sttList.map((stt) => (
            <option
              className="stt-option"
              key={stt.id}
              value={stt.name.toLowerCase()}
            >
              {stt.name}
            </option>
          ))}
        </select>
      </div>
    </label>
  )
}

ComboBox.propTypes = {
  sttList: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      id: PropTypes.number,
    })
  ).isRequired,
}

export default ComboBox
