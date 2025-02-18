import React, { useState } from 'react'

function RegionSelector({
  setErrors,
  errors,
  setTouched,
  touched,
  setProfileInfo,
  profileInfo,
  displayingError,
  validateRegions,
  regionError,
}) {
  const [regional, setRegional] = useState(false)
  const regionKey = 'regions'
  const regionsNames = [
    'Boston',
    'New York',
    'Philadelphia',
    'Atlanta',
    'Chicago',
    'Dallas',
    'Kansas City',
    'Denver',
    'San Francisco',
    'Seattle',
  ]

  const handleRegionChange = (event, regionPK) => {
    const { name, checked } = event.target
    const { [name]: removedError, ...rest } = errors
    const newProfileInfo = { ...profileInfo }
    if (!checked && newProfileInfo.regions.has(regionPK)) {
      newProfileInfo.regions.delete(regionPK)
    } else {
      newProfileInfo.regions.add(regionPK)
    }

    const error = validateRegions(newProfileInfo.regions)

    setErrors({
      ...rest,
      ...(error && { [name]: touched[name] && error }),
    })
    setProfileInfo({ ...newProfileInfo })
  }

  const excludeRegions = (state) => {
    const { regions, ...newState } = state
    return newState
  }

  return (
    <>
      <div className="usa-form-group">
        <fieldset className="usa-fieldset">
          <legend className="usa-label text-bold">
            Do you work for an OFA Regional Office?*
          </legend>
          <div className="usa-radio">
            <input
              className="usa-radio__input"
              id="regional"
              type="radio"
              name="regionalType"
              value="regional"
              onChange={() => {
                if (displayingError) {
                  setTouched({ ...touched, regions: true })
                  setErrors({
                    ...errors,
                    regions: regionError,
                  })
                }
                setProfileInfo({ ...profileInfo, regions: new Set() })
                setRegional(true)
              }}
            />
            <label className="usa-radio__label" htmlFor="regional">
              Yes
            </label>
          </div>
          <div className="usa-radio">
            <input
              className="usa-radio__input"
              id="central"
              type="radio"
              name="regionalType"
              value="central"
              defaultChecked
              onChange={() => {
                setErrors(excludeRegions(errors))
                setTouched(excludeRegions(touched))
                setProfileInfo(excludeRegions(profileInfo))
                setRegional(false)
              }}
            />
            <label className="usa-radio__label" htmlFor="central">
              No
            </label>
          </div>
        </fieldset>
      </div>
      {regional && (
        <div
          className={`usa-form-group ${regionKey in errors ? 'usa-form-group--error' : ''}`}
        >
          <fieldset className="usa-fieldset">
            <legend className="usa-label text-bold">Region(s)*</legend>
            <div>
              Need help?&nbsp;
              <a
                target="_blank"
                rel="noopener noreferrer"
                href="https://www.acf.hhs.gov/oro/regional-offices"
              >
                Lookup region by location.
              </a>
            </div>
            {regionKey in errors && (
              <span className="usa-error-message" id={`regions-error-message`}>
                {errors.regions}
              </span>
            )}
            {regionsNames.map((region, index) => {
              return (
                <div key={region} className="usa-checkbox">
                  <input
                    className={`usa-checkbox__input ${regionKey in errors ? 'usa-input--error' : ''}`}
                    id={region}
                    type="checkbox"
                    name={regionKey}
                    value={region}
                    aria-required="true"
                    onChange={(event) => handleRegionChange(event, index + 1)}
                  />
                  <label
                    className={`usa-checkbox__label ${'regions' in errors ? 'usa-input--error' : ''}`}
                    htmlFor={region}
                  >
                    Region {index + 1} ({region})
                  </label>
                </div>
              )
            })}
          </fieldset>
        </div>
      )}
    </>
  )
}

export default RegionSelector
