import { useSelector } from 'react-redux'
import {
  accountStatusIsApproved,
  selectUserPermissions,
} from '../../selectors/auth'

const isAllowed = (
  { permissions, isApproved },
  requiredPermissions,
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

  return true
}

const PermissionGuard = ({
  children,
  requiresApproval = false,
  requiredPermissions = [],
  notAllowedComponent = null,
}) => {
  const permissions = useSelector(selectUserPermissions)
  const isApproved = useSelector(accountStatusIsApproved)

  return isAllowed(
    { permissions, isApproved },
    requiredPermissions,
    requiresApproval
  )
    ? children
    : notAllowedComponent
}

export default PermissionGuard
