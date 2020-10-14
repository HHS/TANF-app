import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({ sttList }) => {
  const selectRef = useRef()
  useEffect(() => {
    comboBox.init()
    selectRef.current.value = ''
  })
  return (
    <label className="usa-label" htmlFor="sttList">
      Associated State, Tribe, or Territory
      <div className="usa-combo-box">
        <select className="usa-select" name="stt" id="stt" ref={selectRef}>
          {sttList.map((stt) => (
            <option
              className="sttOption"
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
