import React, { useState, useEffect } from 'react'
import '../../assets/Profile.scss'

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
  const [regional, setRegional] = useState(() => {
    return profileInfo?.regions instanceof Set && profileInfo.regions.size > 0
  })

  const [previousRegions, setPreviousRegions] = useState(
    profileInfo?.regions || new Set()
  )

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

  useEffect(() => {
    if (regional) {
      setPreviousRegions(new Set(profileInfo.regions))
    }
  }, [profileInfo.regions, regional])

  const handleRegionChange = (event, regionId) => {
    const { name, checked } = event.target
    const { [name]: removedError, ...rest } = errors

    const currentRegions = new Set(profileInfo.regions || [])

    if (!checked) {
      for (let region of currentRegions) {
        if (region.id === regionId) {
          currentRegions.delete(region)
          break
        }
      }
    } else {
      const regionName = regionsNames[regionId - 1]
      currentRegions.add({ id: regionId, name: regionName })
    }

    const error = validateRegions(currentRegions)

    setErrors({
      ...rest,
      ...(error && { [name]: touched[name] && error }),
    })

    setProfileInfo({
      ...profileInfo,
      regions: currentRegions,
    })
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
              checked={regional}
              onChange={() => {
                if (displayingError) {
                  setTouched({ ...touched, regions: true })
                  setErrors({
                    ...errors,
                    regions: regionError,
                  })
                }
                setProfileInfo({
                  ...profileInfo,
                  regions: previousRegions,
                  hasFRAAccess: true,
                })
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
              checked={!regional}
              onChange={() => {
                setPreviousRegions(profileInfo.regions ?? new Set())
                setErrors(excludeRegions(errors))
                setTouched(excludeRegions(touched))
                setProfileInfo({
                  ...excludeRegions(profileInfo),
                  hasFRAAccess: false,
                })
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
          className={`usa-form-group ${regionKey in errors ? 'usa-form-group--error' : ''} region-selector-wrapper`}
        >
          <fieldset className="usa-fieldset">
            <legend className="usa-label text-bold margin-bottom-1">
              Select Your Regional Office(s)*
            </legend>
            <div className="margin-bottom-3">
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
              const regionId = index + 1
              const isChecked = Array.from(profileInfo?.regions || []).some(
                (r) => r.id === regionId
              )
              return (
                <div key={region} className="usa-checkbox">
                  <input
                    className={`usa-checkbox__input ${regionKey in errors ? 'usa-input--error' : ''}`}
                    id={region}
                    type="checkbox"
                    name={regionKey}
                    value={region}
                    aria-required="true"
                    checked={isChecked}
                    onChange={(event) => handleRegionChange(event, regionId)}
                  />
                  <label
                    className={`usa-checkbox__label ${'regions' in errors ? 'usa-input--error' : ''}`}
                    htmlFor={region}
                  >
                    Region {regionId} ({region})
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
