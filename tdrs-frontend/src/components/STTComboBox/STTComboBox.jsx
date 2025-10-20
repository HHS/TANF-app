import React, { useEffect, useState } from 'react'
import PropTypes from 'prop-types'
import { useDispatch, useSelector } from 'react-redux'
import { fetchSttList } from '../../actions/sttList'
import { ComboBox } from '../Form'
import Modal from '../Modal'
import { toTitleCase } from '../../utils/stringUtils'
import { availableStts } from '../../selectors/stts'

/**
 * @param {function} selectStt - Function to reference and change the
 * selectedStt state.
 * @param {string} selectedStt - The currently selected stt controlled
 * in state elsewhere.
 * @param {function} handleBlur - Runs on blur of combo box element.
 * @param {function} error - Reference to stt errors object.
 */

function STTComboBox({
  selectStt,
  selectedStt = '',
  handleBlur = null,
  error = null,
  sttType,
}) {
  const sttListRequest = useSelector((state) => state?.stts)
  const filteredStts = useSelector(availableStts)
  const dispatch = useDispatch()
  const [numTries, setNumTries] = useState(0)
  const [reachedMaxTries, setReachedMaxTries] = useState(false)

  useEffect(() => {
    const { loading, sttList } = sttListRequest
    if (sttList.length === 0 && numTries <= 3 && !loading) {
      dispatch(fetchSttList())
      setNumTries(numTries + 1)
    } else if (sttList.length === 0 && numTries > 3 && !reachedMaxTries) {
      setReachedMaxTries(true)
    }
  }, [
    dispatch,
    sttListRequest.sttList,
    sttListRequest.loading,
    numTries,
    reachedMaxTries,
  ])

  const onSignOut = () => {
    window.location.href = `${process.env.REACT_APP_BACKEND_URL}/logout/oidc`
  }

  return (
    <>
      {filteredStts.length > 0 && (
        <ComboBox
          name="stt"
          label={
            sttType ? `${toTitleCase(sttType)}*` : 'State, Tribe, or Territory*'
          }
          error={
            error
              ? `A ${sttType || 'state, tribe, or territory'} is required`
              : undefined
          }
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
          {filteredStts?.map(
            (stt) =>
              (sttType == null || stt.type === sttType) && (
                <option className="sttOption" key={stt.id} value={stt.name}>
                  {stt.name}
                </option>
              )
          )}
        </ComboBox>
      )}
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

export default STTComboBox
