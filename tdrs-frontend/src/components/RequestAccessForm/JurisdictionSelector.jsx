function JurisdictionSelector({ setJurisdictionType }) {
  return (
    <div className="usa-form-group">
      <fieldset className="usa-fieldset">
        <legend className="usa-label text-bold">Jurisdiction Type</legend>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="state"
            type="radio"
            name="jurisdictionType"
            value="state"
            defaultChecked
            onChange={() => setJurisdictionType('state')}
          />
          <label className="usa-radio__label" htmlFor="state">
            State
          </label>
        </div>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="tribe"
            type="radio"
            name="jurisdictionType"
            value="tribe"
            onChange={() => setJurisdictionType('tribe')}
          />
          <label className="usa-radio__label" htmlFor="tribe">
            Tribe
          </label>
        </div>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="territory"
            type="radio"
            name="jurisdictionType"
            value="territory"
            onChange={() => setJurisdictionType('territory')}
          />
          <label className="usa-radio__label" htmlFor="territory">
            Territory
          </label>
        </div>
      </fieldset>
    </div>
  )
}

export default JurisdictionSelector
