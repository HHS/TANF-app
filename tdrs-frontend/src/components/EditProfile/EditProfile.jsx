import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import Select from 'react-select'
import { fetchStts } from '../../actions/stts'
import { setAlert, clearAlert } from '../../actions/alert'
import { ALERT_INFO } from '../Notify'

function EditProfile() {
  const sttsLoading = useSelector((state) => state.stts.loading)
  const stts = useSelector((state) => state.stts.stts)
  const dispatch = useDispatch()

  // useEffect(() => {
  //   if (sttsLoading) {
  //     dispatch(setAlert({ heading: 'Please wait...', type: ALERT_INFO }))
  //   } else {
  //     dispatch(clearAlert())
  //   }
  // }, [sttsLoading, dispatch])

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

        <label className="usa-label" htmlFor="stt">
          Associated State, Tribe, or Territory
          <Select
            styles={customStyles}
            name="stt"
            id="stt"
            isLoading={sttsLoading}
            options={stts}
            // theme={(theme) => ({
            //   ...theme,
            //   borderRadius: 0,
            //   colors: {
            //     ...theme.colors,
            //     primary25: 'blue',
            //     primary: 'black',
            //   },
            // })}
          />
        </label>
        <button
          type="submit"
          className="usa-button usa-button--big request-access-button"
          disabled
        >
          Request Access
        </button>
      </form>
    </div>
  )
}

export default EditProfile
