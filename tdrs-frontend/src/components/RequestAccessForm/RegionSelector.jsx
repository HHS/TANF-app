import React, { useState, useEffect, useMemo } from 'react'
import '../../assets/Profile.scss'
import { regionNames, addRegion, removeRegionById } from '../../utils/regions'

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
  originalRegional,
  type,
}) {
  const [previousRegions, setPreviousRegions] = useState(
    profileInfo?.regions || new Set()
  )

  const regionKey = 'regions'
  const isRegionalKey = 'regionalType'

  useEffect(() => {
    if (regional && profileInfo.regions instanceof Set) {
      setPreviousRegions(new Set(profileInfo.regions))
    }
  }, [profileInfo.regions, regional])

  const selectedRegionIds = useMemo(
    () => new Set(Array.from(profileInfo.regions || []).map((r) => r.id)),
    [profileInfo.regions]
  )

  const clearFormError = (prevErrors) => {
    const { form, ...rest } = prevErrors
    return rest
  }

  const handleRegionChange = (event, regionId) => {
    const { name, checked } = event.target
    const regionName = regionNames[regionId - 1]

    const currentRegions = profileInfo.regions || new Set()

    const updatedRegions = checked
      ? addRegion(currentRegions, regionId, regionName)
      : removeRegionById(currentRegions, regionId)

    const error = validateRegions(updatedRegions)

    setErrors((prev) => {
      const { [name]: _, ...rest } = clearFormError(prev)
      return {
        ...rest,
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

  const handleRegionalYes = () => {
    // Clear form error for reset
    setErrors((prev) => clearFormError(prev))
    if (displayingError) {
      setTouched((prev) => ({ ...prev, regions: true, regionalType: true }))
      setErrors((prev) => ({
        ...prev,
        regionalType: null,
        regions: regionError,
      }))
    }
    setProfileInfo((prev) => ({
      ...prev,
      regions: previousRegions,
      hasFRAAccess: true,
    }))
    setRegional(true)
  }

  const handleRegionalNo = () => {
    // Clear form error and regions error when selecting "No"
    setErrors((prev) => {
      const { form, regions, regionalType, ...rest } = prev
      return rest
    })
    setPreviousRegions(new Set())
    setTouched((prev) => excludeRegions(prev))
    setProfileInfo((prev) => ({
      ...excludeRegions(prev),
      regions: new Set(),
      hasFRAAccess: false,
    }))
    setRegional(false)
  }

  const isRegionalButtonDisabled = originalRegional && type === 'profile'

  return (
    <>
      <div className="usa-form-group">
        <fieldset
          className="usa-fieldset"
          disabled={isRegionalButtonDisabled}
          aria-describedby="regional-button-disabled-msg"
        >
          <div
            className={`usa-form-group ${errors[isRegionalKey] ? 'usa-form-group--error' : ''} region-selector-wrapper`}
          >
            <legend className="usa-label text-bold">
              Do you work for an OFA Regional Office?*
            </legend>
            {isRegionalButtonDisabled && (
              <div id="regional-button-disabled-msg" className="usa-hint">
                Regional users cannot remove their regional status through this
                portal.
              </div>
            )}
            {isRegionalKey in errors && (
              <span className="usa-error-message" id="isRegional-error-message">
                {errors[isRegionalKey]}
              </span>
            )}
            <div className="usa-radio">
              <input
                className="usa-radio__input"
                id="regional"
                type="radio"
                name={isRegionalKey}
                value="regional"
                checked={regional === true}
                onChange={handleRegionalYes}
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
                name={isRegionalKey}
                value="central"
                checked={regional === false}
                onChange={handleRegionalNo}
              />
              <label className="usa-radio__label" htmlFor="central">
                No
              </label>
            </div>
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
            {regionNames.map((region, index) => {
              const regionId = index + 1
              const isChecked = selectedRegionIds.has(regionId)
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
