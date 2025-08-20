import React, { useState, useEffect } from 'react'
import '../../assets/Profile.scss'

// Helper functions
const addRegion = (regionsSet, id, name) => {
  const newSet = new Set(regionsSet)
  newSet.add({ id, name })
  return newSet
}

const removeRegionById = (regionsSet, id) => {
  return new Set(Array.from(regionsSet).filter((r) => r.id !== id))
}

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
  regional,
  setRegional,
}) {
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
    const regionName = regionsNames[regionId - 1]

    const currentRegions = profileInfo.regions || new Set()

    const updatedRegions = checked
      ? addRegion(currentRegions, regionId, regionName)
      : removeRegionById(currentRegions, regionId)

    const error = validateRegions(updatedRegions)

    setErrors((prev) => {
      const { [name]: removed, ...rest } = prev
      // Only remove 'form' if it's already present
      const { form, ...errorsWithoutForm } = rest
      return {
        ...errorsWithoutForm,
        ...(error && {
          [name]: touched[name] && regionError,
        }),
      }
    })

    setProfileInfo((prev) => ({
      ...prev,
      regions: updatedRegions,
    }))
  }

  const excludeRegions = (state) => {
    const { regions, form, ...rest } = state
    return rest
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
                // Clear form error for reset
                setErrors((prev) => {
                  const { form, ...rest } = prev
                  return form ? rest : prev
                })

                if (displayingError) {
                  setTouched((prev) => ({ ...prev, regions: true }))
                  setErrors((prev) => ({
                    ...prev,
                    regions: regionError,
                  }))
                }
                setProfileInfo((prev) => ({
                  ...prev,
                  regions: previousRegions,
                  hasFRAAccess: true,
                }))
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
                // Clear form error on change
                setErrors((prev) => {
                  const { form, ...rest } = excludeRegions(prev)
                  return form ? rest : prev
                })

                setPreviousRegions(profileInfo.regions ?? new Set())
                setTouched((prev) => excludeRegions(prev))
                setProfileInfo((prev) => ({
                  ...excludeRegions(prev),
                  regions: new Set(),
                  hasFRAAccess: false,
                }))
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
