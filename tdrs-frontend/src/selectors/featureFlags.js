export const selectFeatureFlags = (state) => state.featureFlags?.flags

export const getFlagOrDefault = (searchName, allFlags = []) =>
  allFlags.find((f) => f.feature_name === searchName) || {
    feature_name: searchName,
    enabled: false,
    config: {},
    description: '',
  }
