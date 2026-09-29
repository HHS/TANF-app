"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState, type MouseEvent } from "react";
import {
  AdminNavAppearanceIcon,
  AdminNavApprovalIcon,
  AdminNavCollapseIcon,
  AdminNavDashboardIcon,
  AdminNavDataFilesIcon,
  AdminNavEtlIcon,
  AdminNavFeatureFlagsIcon,
  AdminNavFeedbackIcon,
  AdminNavHomeIcon,
  AdminNavLogEntriesIcon,
  AdminNavParsersIcon,
  AdminNavPeriodicTasksIcon,
  AdminNavReportsIcon,
  AdminNavSearchIcon,
  AdminNavSearchIndexesIcon,
  AdminNavSecurityIcon,
  AdminNavSttsIcon,
  AdminNavUsersIcon,
  type AdminNavIconProps,
} from "@/components/icons/admin-nav-icons";
import {
  ADMIN_DASHBOARD_NAV_ITEMS,
  ADMIN_PRIMARY_NAV_ITEMS,
  getDefaultExpandedAdminNavIds,
  getAdminNavigationTitle,
  getVisibleAdminNavItems,
  isAdminNavItemActive,
  type AdminNavIconName,
  type AdminNavItem,
  type AdminRoleValue,
} from "@/lib/admin-navigation";

function NavIcon({ name }: { name?: AdminNavIconName }) {
  if (!name) {
    return null;
  }

  return getIcon(name, {
    className: "admin-sidenav__icon",
    "aria-hidden": true,
    focusable: "false",
  });
}

function getIcon(name: AdminNavIconName, iconProps: AdminNavIconProps) {
  switch (name) {
    case "appearance":
      return <AdminNavAppearanceIcon {...iconProps} />;
    case "approval":
      return <AdminNavApprovalIcon {...iconProps} />;
    case "collapse":
      return <AdminNavCollapseIcon {...iconProps} />;
    case "dashboard":
      return <AdminNavDashboardIcon {...iconProps} />;
    case "data-files":
      return <AdminNavDataFilesIcon {...iconProps} />;
    case "etl":
      return <AdminNavEtlIcon {...iconProps} />;
    case "feature-flags":
      return <AdminNavFeatureFlagsIcon {...iconProps} />;
    case "feedback":
      return <AdminNavFeedbackIcon {...iconProps} />;
    case "home":
      return <AdminNavHomeIcon {...iconProps} />;
    case "log-entries":
      return <AdminNavLogEntriesIcon {...iconProps} />;
    case "parsers":
      return <AdminNavParsersIcon {...iconProps} />;
    case "periodic-tasks":
      return <AdminNavPeriodicTasksIcon {...iconProps} />;
    case "reports":
      return <AdminNavReportsIcon {...iconProps} />;
    case "search":
      return <AdminNavSearchIcon {...iconProps} />;
    case "search-indexes":
      return <AdminNavSearchIndexesIcon {...iconProps} />;
    case "security":
      return <AdminNavSecurityIcon {...iconProps} />;
    case "stts":
      return <AdminNavSttsIcon {...iconProps} />;
    case "users":
      return <AdminNavUsersIcon {...iconProps} />;
  }

  const exhaustiveCheck: never = name;
  return exhaustiveCheck;
}

function navItemMatchesSearch(item: AdminNavItem, query: string) {
  return item.label.toLowerCase().includes(query);
}

function filterNavItemsBySearch(
  items: readonly AdminNavItem[],
  searchQuery: string
) {
  const query = searchQuery.trim().toLowerCase();

  if (!query) {
    return [...items];
  }

  return items.reduce<AdminNavItem[]>((filteredItems, item) => {
    const childMatches = item.children
      ? filterNavItemsBySearch(item.children, query)
      : [];

    if (navItemMatchesSearch(item, query)) {
      filteredItems.push(item);
    } else if (childMatches.length) {
      filteredItems.push({ ...item, children: childMatches });
    }

    return filteredItems;
  }, []);
}

function NavLink({
  item,
  currentPath,
}: {
  item: AdminNavItem;
  currentPath: string;
}) {
  const linkContent = (
    <>
      <NavIcon name={item.icon} />
      <span className="admin-sidenav__label">{item.label}</span>
    </>
  );

  const isActive = isAdminNavItemActive(currentPath, item);

  if (!item.href || item.disabled) {
    return (
      <span
        className="admin-sidenav__link admin-sidenav__link--disabled"
        aria-disabled="true"
        title="Page not available yet"
      >
        {linkContent}
      </span>
    );
  }

  return (
    <Link
      className="admin-sidenav__link"
      href={item.href}
      aria-current={isActive ? "page" : undefined}
    >
      {linkContent}
    </Link>
  );
}

function NavGroup({
  item,
  currentPath,
  expanded,
  onToggle,
}: {
  item: AdminNavItem;
  currentPath: string;
  expanded: boolean;
  onToggle: () => void;
}) {
  const groupId = `admin-nav-group-${item.id}`;
  const isActive = isAdminNavItemActive(currentPath, item);

  return (
    <div className="admin-sidenav__group">
      <button
        className="admin-sidenav__group-button"
        type="button"
        aria-expanded={expanded}
        aria-controls={groupId}
        data-active={isActive ? "true" : undefined}
        onClick={onToggle}
      >
        <NavIcon name={item.icon} />
        <span className="admin-sidenav__label">{item.label}</span>
        <span className="admin-sidenav__chevron" aria-hidden="true" />
      </button>
      <ul className="admin-sidenav__children" id={groupId} hidden={!expanded}>
        {item.children?.map((child) => (
          <li key={child.id}>
            <NavLink item={child} currentPath={currentPath} />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function AdminNavigation({
  roles,
  hasDjangoAdminAccess = false,
}: {
  roles?: readonly AdminRoleValue[] | null;
  hasDjangoAdminAccess?: boolean;
}) {
  const currentPath = usePathname() || "/";
  const navigationTitle = useMemo(
    () => getAdminNavigationTitle(roles, hasDjangoAdminAccess),
    [roles, hasDjangoAdminAccess]
  );
  const primaryItems = useMemo(
    () =>
      getVisibleAdminNavItems(
        roles,
        ADMIN_PRIMARY_NAV_ITEMS,
        hasDjangoAdminAccess
      ),
    [roles, hasDjangoAdminAccess]
  );
  const dashboardItems = useMemo(
    () =>
      getVisibleAdminNavItems(
        roles,
        ADMIN_DASHBOARD_NAV_ITEMS,
        hasDjangoAdminAccess
      ),
    [roles, hasDjangoAdminAccess]
  );
  const defaultExpandedIds = useMemo(
    () => getDefaultExpandedAdminNavIds(currentPath, primaryItems),
    [currentPath, primaryItems]
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isHoverExpansionDisabled, setIsHoverExpansionDisabled] =
    useState(false);
  const [expandedIds, setExpandedIds] = useState(defaultExpandedIds);
  const filteredPrimaryItems = useMemo(
    () => filterNavItemsBySearch(primaryItems, searchQuery),
    [primaryItems, searchQuery]
  );
  const filteredDashboardItems = useMemo(
    () => filterNavItemsBySearch(dashboardItems, searchQuery),
    [dashboardItems, searchQuery]
  );
  const openIds = new Set(expandedIds);
  const hasSearchResults =
    filteredPrimaryItems.length > 0 || filteredDashboardItems.length > 0;

  function toggleExpanded(id: string) {
    setExpandedIds((currentIds) =>
      currentIds.includes(id)
        ? currentIds.filter((currentId) => currentId !== id)
        : [...currentIds, id]
    );
  }

  function toggleCollapsed(event: MouseEvent<HTMLButtonElement>) {
    const nextCollapsed = !isCollapsed;

    setIsCollapsed(nextCollapsed);
    setIsHoverExpansionDisabled(nextCollapsed);

    if (nextCollapsed) {
      event.currentTarget.blur();
    }
  }

  return (
    <aside
      className="admin-sidenav"
      aria-label="Admin navigation"
      data-collapsed={isCollapsed ? "true" : undefined}
      data-hover-expansion-disabled={
        isHoverExpansionDisabled ? "true" : undefined
      }
      onMouseLeave={() => setIsHoverExpansionDisabled(false)}
    >
      <button
        className="admin-sidenav__mobile-toggle usa-button usa-button--outline"
        type="button"
        aria-expanded={isMenuOpen}
        aria-controls="admin-sidenav-menu"
        onClick={() => setIsMenuOpen((open) => !open)}
      >
        Menu
      </button>
      <nav
        className="admin-sidenav__nav"
        id="admin-sidenav-menu"
        data-open={isMenuOpen ? "true" : undefined}
      >
        <div className="admin-sidenav__search" role="search">
          <label className="usa-sr-only" htmlFor="admin-nav-search">
            Search navigation
          </label>
          <NavIcon name="search" />
          <input
            className="admin-sidenav__search-input"
            id="admin-nav-search"
            type="search"
            placeholder="Search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
          />
        </div>

        <p className="admin-sidenav__title">
          <span className="admin-sidenav__label">{navigationTitle}</span>
        </p>

        <ul className="admin-sidenav__list">
          {filteredPrimaryItems.map((item) => (
            <li
              key={item.id}
              data-separator-before={item.separatorBefore || undefined}
            >
              {item.children?.length ? (
                <NavGroup
                  item={item}
                  currentPath={currentPath}
                  expanded={openIds.has(item.id)}
                  onToggle={() => toggleExpanded(item.id)}
                />
              ) : (
                <NavLink item={item} currentPath={currentPath} />
              )}
            </li>
          ))}
        </ul>

        {filteredDashboardItems.length > 0 ? (
          <div className="admin-sidenav__section admin-sidenav__section--dashboards">
            <p className="admin-sidenav__section-title">
              <span className="admin-sidenav__label">Dashboards</span>
            </p>
            <ul className="admin-sidenav__list">
              {filteredDashboardItems.map((item) => (
                <li key={item.id}>
                  <NavLink item={item} currentPath={currentPath} />
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {!hasSearchResults ? (
          <p className="admin-sidenav__empty" aria-live="polite">
            <span className="admin-sidenav__label">No menu items found.</span>
          </p>
        ) : null}

        <button
          className="admin-sidenav__collapse-button"
          type="button"
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          onClick={toggleCollapsed}
        >
          <NavIcon name="collapse" />
          <span className="admin-sidenav__label">
            {isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
          </span>
        </button>
      </nav>
    </aside>
  );
}
