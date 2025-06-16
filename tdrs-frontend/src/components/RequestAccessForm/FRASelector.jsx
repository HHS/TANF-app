function FRASelector({ hasFRAData, setHasFRAData, error, setErrors }) {
  const handleRadioChange = (value) => {
    setHasFRAData(value)

    // clear any error messages
    setErrors((errs) => {
      const { hasFRAData, ...rest } = errs
      return rest
    })
  }

  return (
    <div className={`usa-form-group ${error ? 'usa-form-group--error' : ''}`}>
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

        {error && (
          <span className="usa-error-message" id="fra-selector-error-message">
            {error}
          </span>
        )}

        <div className="usa-radio">
          <input
            className="usa-radio__input"
            id="fra-yes"
            type="radio"
            name="hasFRAData"
            value="true"
            defaultChecked
            checked={hasFRAData === true}
            onChange={() => handleRadioChange(true)}
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
            checked={hasFRAData === false}
            onChange={() => handleRadioChange(false)}
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
