import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import comboBox from 'uswds/src/js/components/combo-box'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'

function EditProfile() {
  const stts = useSelector((state) => state.stts.stts)
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchStts())
    comboBox.init()
  }, [dispatch])

  return (
    <div className="grid-container">
      <h1 className="request-access-header font-serif-2xl">Request Access</h1>
      <p className="request-access-secondary">
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <form className="usa-form">
        <label className="usa-label" htmlFor="first-name">
          First name
          <input
            className="usa-input"
            id="first-name"
            name="first-name"
            type="text"
            required
            aria-required="true"
          />
        </label>

        <label className="usa-label" htmlFor="last-name">
          Last name
          <input
            className="usa-input"
            id="last-name"
            name="last-name"
            type="text"
            required
            aria-required="true"
          />
        </label>
        <label className="usa-label" htmlFor="stt">
          Associated State, Tribe, or Territory
          <div className="usa-combo-box">
            <select
              className="usa-select usa-combo-box__select"
              name="stt"
              id="sttList"
            >
              {stts.map((stt) => (
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
        <Button
          type="submit"
          disabled
          size="big"
          className="request-access-button"
        >
          Request Access
        </Button>
      </form>
    </div>
  )
}

export default EditProfile
