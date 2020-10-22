import React from 'react'
import Button from '../Button'
import {Helmet} from "react-helmet"

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
