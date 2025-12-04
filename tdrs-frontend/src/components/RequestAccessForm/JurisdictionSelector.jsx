function JurisdictionSelector({ jurisdictionType, setJurisdictionType }) {
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
            checked={jurisdictionType === 'state'}
            onChange={() => setJurisdictionType('state')}
            onClick={() => setJurisdictionType('state')}
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
            checked={jurisdictionType === 'tribe'}
            onChange={() => setJurisdictionType('tribe')}
            onClick={() => setJurisdictionType('tribe')}
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
            checked={jurisdictionType === 'territory'}
            onChange={() => setJurisdictionType('territory')}
            onClick={() => setJurisdictionType('territory')}
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
