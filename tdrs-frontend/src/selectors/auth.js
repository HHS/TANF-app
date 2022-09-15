const valueIsEmpty = (val) => val === null || val === undefined || val === ''

export const selectUser = (state) => state.auth.user || null

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
  let permissions = []
  roles.forEach((role) => {
    permissions = [...permissions, role['permissions']]
  })
  return permissions
}

export const accountStatusIsInitial = (state) =>
  selectUserAccountApprovalStatus(state) === 'Initial'

export const accountStatusIsAccessRequestSubmitted = (state) =>
  selectUserAccountApprovalStatus(state) === 'Access request'

export const accountStatussIsPending = (state) =>
  selectUserAccountApprovalStatus(state) === 'Pending'

export const accountIsInReview = (state) =>
  accountStatusIsAccessRequestSubmitted(state) || accountStatussIsPending(state)

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
