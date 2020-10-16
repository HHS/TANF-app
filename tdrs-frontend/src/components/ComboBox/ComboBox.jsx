import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({
  sttList,
  setProfileInfo,
  profileInfo,
  selectedStt,
  handleBlur,
}) => {
  const selectRef = useRef()
  useEffect(() => {
    // The combo box was not rendering as a combo box without this line
    comboBox.init()
    // This solved the issue when tabbing through the form on EditProfile,
    // a selection was automatically being made on the first option
    selectRef.current.value = ''
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
          setProfileInfo({ ...profileInfo, stt: e.target.value })
        }}
        value={selectedStt}
      >
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
  )
}

ComboBox.propTypes = {
  sttList: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      id: PropTypes.number,
    })
  ).isRequired,
  setProfileInfo: PropTypes.func.isRequired,
  profileInfo: PropTypes.objectOf(PropTypes.string).isRequired,
  selectedStt: PropTypes.string,
  handleBlur: PropTypes.func.isRequired,
}

ComboBox.defaultProps = {
  selectedStt: '',
}

export default ComboBox
