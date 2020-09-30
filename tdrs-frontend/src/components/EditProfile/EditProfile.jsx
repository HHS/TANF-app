import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Select from 'react-select'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'

function EditProfile() {
  const sttsLoading = useSelector((state) => state.stts.loading)
  const stts = useSelector((state) =>
    state.stts.stts.map((stt) => ({
      value: stt.name.toLowerCase(),
      label: stt.name,
    }))
  )
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchStts())
  }, [dispatch])

  const customStyles = {
    control: (provided, state) => ({
      ...provided,
      border: '1px solid #1b1b1b',
      width: 320,
      height: 40,
      marginTop: '.5rem',
      borderRadius: 0,
    }),
    dropdownIndicator: (provided, state) => ({
      ...provided,
      color: '#1b1b1b',
    }),
    placeholder: (provided, state) => ({
      ...provided,
      color: '#1b1b1b',
    }),
  }

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
        {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
        <label className="usa-label" htmlFor="stt">
          Associated State, Tribe, or Territory
          <Select
            styles={customStyles}
            inputId="stt"
            isLoading={sttsLoading}
            isClearable
            options={stts}
          />
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
