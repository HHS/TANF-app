import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchStts } from '../../actions/stts'
import Button from '../Button'
import {Helmet} from "react-helmet"
import ComboBox from '../ComboBox'

function TitleHeading({title}) {

  return (
    <>
      <Helmet>
        <title>{title} - TDP - TANF Data Portal</title>
      </Helmet>
      <h1 className="request-access-header font-serif-2xl">{title}</h1>
    </>
  )

}

function EditProfile() {
  const stts = useSelector((state) => state.stts.stts)
  const dispatch = useDispatch()

  useEffect(() => {
    dispatch(fetchStts())
  }, [dispatch])

  return (
    <div className="grid-container">
      <TitleHeading title = "Request Access"/>
      <p className="request-access-secondary">
        We need to collect some information before an OFA Admin can grant you
        access
      </p>
      <form className="usa-form">
        <label className="usa-label" htmlFor="first-name">
          First name
          <input
            className="usa-input"
            id="firstName"
            name="firstName"
            type="text"
            required
            aria-required="true"
          />
        </label>

        <label className="usa-label" htmlFor="lastName">
          Last name
          <input
            className="usa-input"
            id="lastName"
            name="lastName"
            type="text"
            required
            aria-required="true"
          />
        </label>
        <ComboBox>
          {stts.map((stt) => (
            <option
              className="sttOption"
              key={stt.id}
              value={stt.name.toLowerCase()}
            >
              {stt.name}
            </option>
          ))}
        </ComboBox>
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
