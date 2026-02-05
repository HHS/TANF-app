const valueIsEmpty = (val) => val === null || val === undefined || val === ''

export const selectUser = (state) => state.auth.user || null

export const selectFeatureFlags = (state) =>
  selectUser(state)?.feature_flags || {}

// could memoize these with `createSelector` from `reselect`
export const selectUserAccountApprovalStatus = (state) =>
  selectUser(state)?.['account_approval_status']

export const selectUserRoles = (state) => selectUser(state)?.['roles'] || []

export const selectPrimaryUserRole = (state) => {
  const roles = selectUserRoles(state)
  if (roles.length > 0) {
    return roles[0]
  }
  return null
}

export const selectUserPermissions = (state) => {
  const roles = selectUserRoles(state)
  const userLevelPermissions = selectUser(state)?.permissions || []

  let permissions = []
  roles.forEach((role) => {
    permissions = [...permissions, ...role['permissions']]
  })
  permissions = [...permissions, ...userLevelPermissions]

  return permissions.map((p) => p.codename)
}

export const accountStatusIsInitial = (state) =>
  selectUserAccountApprovalStatus(state) === 'Initial'

export const accountStatusIsAccessRequestSubmitted = (state) =>
  selectUserAccountApprovalStatus(state) === 'Access request'

export const accountStatussIsPending = (state) =>
  selectUserAccountApprovalStatus(state) === 'Pending'

export const accountIsInReview = (state) =>
  accountStatusIsAccessRequestSubmitted(state) ||
  accountStatussIsPending(state) ||
  (accountStatusIsApproved(state) && selectUserRoles(state).length === 0)

export const accountStatusIsApproved = (state) =>
  selectUserAccountApprovalStatus(state) === 'Approved'

export const accountStatusIsDenied = (state) =>
  selectUserAccountApprovalStatus(state) === 'Denied'

export const accountStatusIsDeactivated = (state) =>
  selectUserAccountApprovalStatus(state) === 'Deactivated'

export const accountIsMissingAccessRequest = (state) =>
  valueIsEmpty(selectUser(state)) ||
  valueIsEmpty(selectUserAccountApprovalStatus(state)) ||
  accountStatusIsInitial(state) ||
  accountStatusIsDenied(state)

export const accountHasPendingProfileChange = (state) =>
  (selectUser(state)?.pending_requests ?? 0) > 0

export const accountCanViewAdmin = (state) =>
  accountStatusIsApproved(state) &&
  [
    'Developer',
    'OFA System Admin',
    'ACF OCIO',
    'OFA Admin',
    'DIGIT Team',
    'System Owner',
  ].includes(selectPrimaryUserRole(state)?.name)

export const accountCanViewGrafana = (state) =>
  accountStatusIsApproved(state) &&
  ['OFA System Admin', 'Developer', 'DIGIT Team'].includes(
    selectPrimaryUserRole(state)?.name
  )

export const accountCanViewAlerts = (state) =>
  accountStatusIsApproved(state) &&
  ['OFA System Admin', 'Developer'].includes(selectPrimaryUserRole(state)?.name)

export const accountIsRegionalStaff = (state) =>
  accountStatusIsApproved(state) &&
  selectPrimaryUserRole(state)?.name === 'OFA Regional Staff'

export const accountCanSelectStt = (state) =>
  accountStatusIsApproved(state) &&
  [
    'OFA System Admin',
    'OFA Admin',
    'DIGIT Team',
    'OFA Regional Staff',
  ].includes(selectPrimaryUserRole(state)?.name)

export const accountCanViewFeedbackReports = (state) =>
  accountStatusIsApproved(state) &&
  selectUserPermissions(state).includes('view_reportsource') &&
  selectUserPermissions(state).includes('add_reportsource')
