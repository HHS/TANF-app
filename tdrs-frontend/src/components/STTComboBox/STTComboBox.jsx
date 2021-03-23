import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fetchSttList } from '../../actions/sttList'
import ComboBox from '../ComboBox'

/**
 * @param {function} selectStt - Function to reference and change the
 * selectedStt state.
 * @param {string} selectedStt - The currently selected stt controlled
 * in state elsewhere.
 * @param {function} handleBlur - Runs on blur of combo box element.
 * @param {function} error - Reference to stt errors object.
 */
function STTComboBox({ selectStt, selectedStt, handleBlur, error }) {
  const sttList = useSelector((state) => state.stts.sttList)
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchSttList())
  }, [dispatch])

  return (
    <ComboBox
      name="stt"
      label="Associated State, Tribe, or Territory"
      error={error}
      handleSelect={selectStt}
      selected={selectedStt}
      handleBlur={handleBlur}
      placeholder="- Select or Search -"
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
    </ComboBox>
  )
}

STTComboBox.propTypes = {
  selectStt: PropTypes.func.isRequired,
  handleBlur: PropTypes.func,
  selectedStt: PropTypes.string,
  error: PropTypes.string,
}

STTComboBox.defaultProps = {
  handleBlur: null,
  selectedStt: '',
  error: null,
}
export default STTComboBox
