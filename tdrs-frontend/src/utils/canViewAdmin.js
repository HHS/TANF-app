const isMemberOfOne = (user, groupNames) =>
  user?.roles?.some((role) => groupNames.includes(role.name))

const userAccessRequestApproved = (user) =>
  user?.['access_request'] && user?.roles?.length > 0

const canViewAdmin = (user) =>
  userAccessRequestApproved(user) &&
  isMemberOfOne(user, [
    'Developer',
    'OFA System Admin',
    'ACF OCIO',
    'OFA Admin',
  ])

export default canViewAdmin
