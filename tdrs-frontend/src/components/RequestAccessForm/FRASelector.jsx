function FRASelector({ hasFRAData, setHasFRAData }) {
  return (
    <div className="usa-form-group">
      <fieldset className="usa-fieldset">
        <legend className="usa-label text-bold text-no-wrap">
          Will you be reporting Fiscal Responsibility Act (FRA) data files?*
        </legend>
        <p className="text-no-wrap margin-y-2px">
          Unsure?{' '}
          <a href="https://tdp-project-updates.app.cloud.gov/knowledge-center/submitting-fra-data.html">
            Learn about FRA data file reporting
          </a>
        </p>
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
