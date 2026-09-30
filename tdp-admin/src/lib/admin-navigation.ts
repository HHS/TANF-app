export const OFA_SYSTEM_ADMIN_ROLE = "OFA System Admin";
export const OFA_ADMIN_ROLE = "OFA Admin";
export const ACF_OCIO_ROLE = "ACF OCIO";
export const DIGIT_TEAM_ROLE = "DIGIT Team";
export const DEVELOPER_ROLE = "Developer";

export type AdminNavIconName =
  | "appearance"
  | "approval"
  | "collapse"
  | "dashboard"
  | "data-files"
  | "etl"
  | "feature-flags"
  | "feedback"
  | "home"
  | "log-entries"
  | "parsers"
  | "periodic-tasks"
  | "reports"
  | "search"
  | "search-indexes"
  | "security"
  | "stts"
  | "users";

export type AdminRoleValue =
  | string
  | {
      name?: string | null;
      [key: string]: unknown;
    };

export type AdminNavItem = {
  id: string;
  label: string;
  href?: string;
  disabled?: boolean;
  defaultExpanded?: boolean;
  icon?: AdminNavIconName;
  separatorBefore?: boolean;
  allowedRoles?: readonly string[];
  children?: readonly AdminNavItem[];
};

const ADMIN_ACCESS_ROLES = [
  OFA_SYSTEM_ADMIN_ROLE,
  DEVELOPER_ROLE,
  ACF_OCIO_ROLE,
  DIGIT_TEAM_ROLE,
  OFA_ADMIN_ROLE,
] as const;
const SYSTEM_ADMIN_NAV_ROLES = [OFA_SYSTEM_ADMIN_ROLE, DEVELOPER_ROLE] as const;
const OFA_ADMIN_NAV_ROLES = [
  OFA_SYSTEM_ADMIN_ROLE,
  DEVELOPER_ROLE,
  OFA_ADMIN_ROLE,
] as const;
const DIGIT_NAV_ROLES = [
  OFA_SYSTEM_ADMIN_ROLE,
  DEVELOPER_ROLE,
  DIGIT_TEAM_ROLE,
] as const;
const OFA_AND_DIGIT_NAV_ROLES = [
  OFA_SYSTEM_ADMIN_ROLE,
  DEVELOPER_ROLE,
  DIGIT_TEAM_ROLE,
  OFA_ADMIN_ROLE,
] as const;
const SECURITY_NAV_ROLES = [
  OFA_SYSTEM_ADMIN_ROLE,
  DEVELOPER_ROLE,
  ACF_OCIO_ROLE,
  OFA_ADMIN_ROLE,
] as const;

export const ADMIN_PRIMARY_NAV_ITEMS = [
  {
    id: "home",
    label: "Home",
    href: "/dashboard",
    icon: "home",
    allowedRoles: ADMIN_ACCESS_ROLES,
  },
  {
    id: "users",
    label: "Users",
    icon: "users",
    defaultExpanded: true,
    allowedRoles: OFA_ADMIN_NAV_ROLES,
    children: [
      {
        id: "user-accounts",
        label: "User accounts",
        href: "/users",
      },
      {
        id: "requests-authorization",
        label: "Requests & Authorization",
        disabled: true,
        icon: "approval",
      },
      {
        id: "feedback",
        label: "Feedback",
        disabled: true,
        icon: "feedback",
      },
    ],
  },
  {
    id: "log-entries",
    label: "Log Entries",
    disabled: true,
    icon: "log-entries",
    allowedRoles: OFA_ADMIN_NAV_ROLES,
  },
  {
    id: "data-files",
    label: "Data Files",
    disabled: true,
    icon: "data-files",
    separatorBefore: true,
    allowedRoles: OFA_AND_DIGIT_NAV_ROLES,
  },
  {
    id: "etl",
    label: "ETL",
    disabled: true,
    icon: "etl",
    allowedRoles: DIGIT_NAV_ROLES,
  },
  {
    id: "feature-flags",
    label: "Feature Flags",
    disabled: true,
    icon: "feature-flags",
    allowedRoles: SYSTEM_ADMIN_NAV_ROLES,
  },
  {
    id: "parsers",
    label: "Parsers",
    disabled: true,
    icon: "parsers",
    allowedRoles: DIGIT_NAV_ROLES,
  },
  {
    id: "periodic-tasks",
    label: "Periodic Tasks",
    disabled: true,
    icon: "periodic-tasks",
    allowedRoles: SYSTEM_ADMIN_NAV_ROLES,
  },
  {
    id: "reports",
    label: "Reports",
    disabled: true,
    icon: "reports",
    allowedRoles: OFA_AND_DIGIT_NAV_ROLES,
  },
  {
    id: "search-indexes",
    label: "Search Indexes",
    disabled: true,
    icon: "search-indexes",
    allowedRoles: DIGIT_NAV_ROLES,
  },
  {
    id: "security",
    label: "Security",
    disabled: true,
    icon: "security",
    allowedRoles: SECURITY_NAV_ROLES,
  },
  {
    id: "stts",
    label: "STTs",
    disabled: true,
    icon: "stts",
    allowedRoles: OFA_AND_DIGIT_NAV_ROLES,
  },
  {
    id: "appearance",
    label: "Appearance",
    disabled: true,
    icon: "appearance",
    allowedRoles: SYSTEM_ADMIN_NAV_ROLES,
  },
] as const satisfies readonly AdminNavItem[];

export const ADMIN_DASHBOARD_NAV_ITEMS = [
  {
    id: "acf-ocio-dashboard",
    label: "ACF OCIO",
    disabled: true,
    allowedRoles: SYSTEM_ADMIN_NAV_ROLES,
  },
  {
    id: "digit-team-dashboard",
    label: "DIGIT Team",
    disabled: true,
    allowedRoles: SYSTEM_ADMIN_NAV_ROLES,
  },
  {
    id: "ofa-admin-dashboard",
    label: "OFA Admin",
    disabled: true,
    allowedRoles: SYSTEM_ADMIN_NAV_ROLES,
  },
] as const satisfies readonly AdminNavItem[];

export const ADMIN_NAV_ITEMS = ADMIN_PRIMARY_NAV_ITEMS;

export function getAdminRoleNames(roles?: readonly AdminRoleValue[] | null) {
  if (!roles?.length) {
    return [];
  }

  return roles
    .map((role) => (typeof role === "string" ? role : role.name))
    .filter((roleName): roleName is string => Boolean(roleName?.trim()))
    .map((roleName) => roleName.trim());
}

function hasAllowedRole(
  roleNames: readonly string[],
  allowedRoles?: readonly string[]
) {
  if (!allowedRoles?.length) {
    return true;
  }

  return allowedRoles.some((role) => roleNames.includes(role));
}

export function getVisibleAdminNavItems(
  roleValues?: readonly AdminRoleValue[] | null,
  items: readonly AdminNavItem[] = ADMIN_PRIMARY_NAV_ITEMS,
  hasDjangoAdminAccess = false
): AdminNavItem[] {
  const roleNames = getAdminRoleNames(roleValues);

  return items
    .filter(
      (item) =>
        hasDjangoAdminAccess || hasAllowedRole(roleNames, item.allowedRoles)
    )
    .map((item) => {
      const visibleChildren = item.children
        ? getVisibleAdminNavItems(
            roleNames,
            item.children,
            hasDjangoAdminAccess
          )
        : undefined;

      return {
        ...item,
        children: visibleChildren,
      };
    })
    .filter((item) => item.href || item.disabled || item.children?.length);
}

export function isAdminNavItemActive(currentPath: string, item: AdminNavItem) {
  if (item.children?.some((child) => isAdminNavItemActive(currentPath, child))) {
    return true;
  }

  if (!item.href || item.disabled) {
    return false;
  }

  if (item.href === "/") {
    return currentPath === "/";
  }

  return currentPath === item.href || currentPath.startsWith(`${item.href}/`);
}

export function getDefaultExpandedAdminNavIds(
  currentPath: string,
  items: readonly AdminNavItem[]
) {
  return items
    .filter(
      (item) =>
        item.defaultExpanded ||
        item.children?.some((child) => isAdminNavItemActive(currentPath, child))
    )
    .map((item) => item.id);
}

export function getAdminNavigationTitle(
  roles?: readonly AdminRoleValue[] | null,
  hasDjangoAdminAccess = false
) {
  const roleNames = getAdminRoleNames(roles);

  if (
    hasDjangoAdminAccess ||
    roleNames.includes(OFA_SYSTEM_ADMIN_ROLE) ||
    roleNames.includes(DEVELOPER_ROLE)
  ) {
    return "System Admin";
  }

  if (roleNames.includes(ACF_OCIO_ROLE)) {
    return "ACF OCIO";
  }

  if (roleNames.includes(DIGIT_TEAM_ROLE)) {
    return "DIGIT Team";
  }

  if (roleNames.includes(OFA_ADMIN_ROLE)) {
    return "OFA Admin";
  }

  return "Admin";
}
