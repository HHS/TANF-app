function FRASelector({ setHasFRAData }) {
  return (
    <div className="usa-form-group">
      <fieldset className="usa-fieldset">
        <legend className="usa-label text-bold">Has FRA Data</legend>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="yes"
            type="radio"
            name="hasFRAData"
            value="yes"
            defaultChecked
            onChange={() => setHasFRAData('yes')}
          />
          <label className="usa-radio__label" htmlFor="yes">
            Yes
          </label>
        </div>
        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="no"
            type="radio"
            name="hasFRAData"
            value="no"
            onChange={() => setHasFRAData('no')}
          />
          <label className="usa-radio__label" htmlFor="no">
            No
          </label>
        </div>
      </fieldset>
    </div>
  )
}

export default FRASelector
