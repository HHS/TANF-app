import { useSelector } from 'react-redux'
import {
  accountStatusIsApproved,
  selectUserPermissions,
  selectPrimaryUserRole,
} from '../../selectors/auth'
import {
  getFlagOrDefault,
  selectFeatureFlags,
} from '../../selectors/featureFlags'

const isAllowed = (
  { permissions, isApproved, featureFlags, role },
  requiredPermissions,
  requiredFeatureFlags,
  requiresApproval
) => {
  if (requiresApproval && !isApproved) {
    return false
  }

  if (!requiredPermissions) {
    return true
  }

  for (var i = 0; i < requiredPermissions.length; i++) {
    if (!permissions.includes(requiredPermissions[i])) {
      return false
    }
  }

  if (!requiredFeatureFlags) {
    return true
  }

  const isSystemAdmin = role?.name === 'OFA System Admin'
  if (isSystemAdmin) return true

  for (var f = 0; f < requiredFeatureFlags.length; f++) {
    const featureFlag = getFlagOrDefault(requiredFeatureFlags[f], featureFlags)
    if (!featureFlag || featureFlag.enabled !== true) {
      return false
    }
  }

  return true
}

const PermissionGuard = ({
  children,
  requiresApproval = false,
  requiredPermissions = [],
  requiredFeatureFlags = [],
  notAllowedComponent = null,
}) => {
  const permissions = useSelector(selectUserPermissions)
  const isApproved = useSelector(accountStatusIsApproved)
  const featureFlags = useSelector(selectFeatureFlags)
  const role = useSelector(selectPrimaryUserRole)

  return isAllowed(
    { permissions, isApproved, featureFlags, role },
    requiredPermissions,
    requiredFeatureFlags,
    requiresApproval
  )
    ? children
    : notAllowedComponent
}

export default PermissionGuard
