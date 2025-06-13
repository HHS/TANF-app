function FRASelector({ hasFRAData, setHasFRAData }) {
  return (
    <div className="usa-form-group">
      <fieldset className="usa-fieldset">
        <legend className="usa-label text-bold">Has FRA Data</legend>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="fra-yes"
            type="radio"
            name="hasFRAData"
            value="true"
            defaultChecked
            checked={hasFRAData}
            onChange={() => setHasFRAData(true)}
          />
          <label className="usa-radio__label" htmlFor="fra-yes">
            Yes
          </label>
        </div>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="fra-no"
            type="radio"
            name="hasFRAData"
            value="false"
            checked={!hasFRAData}
            onChange={() => setHasFRAData(false)}
          />
          <label className="usa-radio__label" htmlFor="fra-no">
            No
          </label>
        </div>
      </fieldset>
    </div>
  )
}

export default FRASelector
