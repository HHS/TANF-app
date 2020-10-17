import React, { useEffect, useRef } from 'react'
import PropTypes from 'prop-types'
import comboBox from 'uswds/src/js/components/combo-box'

const ComboBox = ({ sttList, setStt, selectedStt, handleBlur, sttError }) => {
  const selectRef = useRef()
  useEffect(() => {
    // The combo box was not rendering as a combo box without this line
    comboBox.init()
    // This solved the issue when tabbing through the form on EditProfile,
    // a selection was automatically being made on the first option
    selectRef.current.value = ''

    // const input = document.querySelector('.usa-combo-box__input')

    // if (sttError) {
    //   input.classList.add('usa-combo-box__input--error')
    // }

    // if (!sttError) {
    //   input.classList.remove('usa-combo-box__input--error')
    // }
  })

  return (
    <div className="usa-combo-box usa-combo-box--error">
      {/* eslint-disable-next-line */}
      <select
        className="usa-select"
        name="stt"
        id="stt"
        ref={selectRef}
        onChange={(e) => {
          handleBlur(e)
          setStt(e.target.value)
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
  setStt: PropTypes.func.isRequired,
  selectedStt: PropTypes.string,
  handleBlur: PropTypes.func.isRequired,
  sttError: PropTypes.string,
}

ComboBox.defaultProps = {
  selectedStt: '',
  sttError: '',
}

export default ComboBox
