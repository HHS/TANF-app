export const FRA_SUBMISSION_YEARS_FEATURE_FLAG = 'fra_submission_years'

export const selectFeatureFlags = (state) => state.featureFlags?.flags || []

export const getFlagOrDefault = (searchName, allFlags = []) =>
  allFlags.find((f) => f.feature_name === searchName) || {
    feature_name: searchName,
    enabled: false,
    config: {},
    description: '',
  }

export const isFeatureActiveForYear = (searchName, year, allFlags = []) => {
  const featureFlag = getFlagOrDefault(searchName, allFlags)
  const activeYears = featureFlag.config?.activeYears
  const numericYear = Number(year)

  return (
    featureFlag.enabled &&
    Array.isArray(activeYears) &&
    Number.isInteger(numericYear) &&
    activeYears.includes(numericYear)
  )
}
