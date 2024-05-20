import React, { useEffect, useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fetchSttList } from '../../actions/sttList'
import ComboBox from '../ComboBox'
import Modal from '../Modal'
import { toTitleCase } from '../../utils/stringUtils'

/**
 * @param {function} selectStt - Function to reference and change the
 * selectedStt state.
 * @param {string} selectedStt - The currently selected stt controlled
 * in state elsewhere.
 * @param {function} handleBlur - Runs on blur of combo box element.
 * @param {function} error - Reference to stt errors object.
 */

function STTComboBox({ selectStt, selectedStt, handleBlur, error, sttType }) {
  const sttListRequest = useSelector((state) => state?.stts)
  const dispatch = useDispatch()
  const [numTries, setNumTries] = useState(0)
  const [reachedMaxTries, setReachedMaxTries] = useState(false)

  useEffect(() => {
    if (
      sttListRequest.sttList.length === 0 &&
      numTries <= 3 &&
      !sttListRequest.loading
    ) {
      dispatch(fetchSttList())
      setNumTries(numTries + 1)
    } else if (
      sttListRequest.sttList.length === 0 &&
      numTries > 3 &&
      !reachedMaxTries
    ) {
      setReachedMaxTries(true)
    }
  }, [dispatch, sttListRequest.sttList, numTries, reachedMaxTries])

  const onSignOut = () => {
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  return (
    <>
      <ComboBox
        name="stt"
        label={
          sttType
            ? toTitleCase(sttType)
            : 'Associated State, Tribe, or Territory*'
        }
        error={error ? 'A state, tribe, or territory is required' : undefined}
        handleSelect={selectStt}
        selected={selectedStt}
        handleBlur={handleBlur}
        placeholder="- Select or Search -"
        aria-required="true"
        autoComplete={false}
      >
        <option value="" disabled hidden>
          - Select or Search -
        </option>
        {sttListRequest.sttList.map(
          (stt) =>
            (sttType == null || stt.type === sttType) && (
              <option className="sttOption" key={stt.id} value={stt.name}>
                {stt.name}
              </option>
            )
        )}
      </ComboBox>
      <Modal
        title="TDP systems are currently experiencing technical difficulties."
        message="Please sign out and try signing in again. If the issue persists contact support at tanfdata@acf.hhs.gov."
        isVisible={reachedMaxTries}
        buttons={[
          {
            key: '1',
            text: 'Sign Out Now',
            onClick: () => {
              onSignOut()
            },
          },
        ]}
      />
    </>
  )
}

STTComboBox.propTypes = {
  selectStt: PropTypes.func.isRequired,
  handleBlur: PropTypes.func,
  selectedStt: PropTypes.string,
  error: PropTypes.bool,
}

STTComboBox.defaultProps = {
  handleBlur: null,
  selectedStt: '',
  error: null,
}
export default STTComboBox
