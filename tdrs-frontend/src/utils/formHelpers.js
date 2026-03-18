// utils/formHelpers.js

export const FORM_TYPES = Object.freeze({
  ACCESS_REQUEST: 'access request',
  PROFILE: 'profile',
})

export const getInitialProfileInfo = (
  initialValues,
  isAMSUser,
  editMode,
  alreadyHasFRAAccess
) => {
  let hasFRAAccess = null
  const isTribal = initialValues.jurisdictionType === 'tribe'

  if (editMode) {
    hasFRAAccess = alreadyHasFRAAccess
  } else if (isAMSUser || isTribal) {
    hasFRAAccess = false
  } else if (typeof initialValues.hasFRAAccess !== 'undefined') {
    hasFRAAccess = initialValues.hasFRAAccess
  }

  const normalizeRegions = (regions) => {
    if (regions instanceof Set) {
      return new Set(regions)
    }

    if (Array.isArray(regions)) {
      return new Set(regions)
    }

    return new Set()
  }

  return {
    firstName: initialValues.firstName || '',
    lastName: initialValues.lastName || '',
    stt: initialValues.stt || '',
    hasFRAAccess,
    regions: normalizeRegions(initialValues.regions),
  }
}

export const clearFormError = (prevErrors) => {
  const { form, ...rest } = prevErrors
  return rest
}
