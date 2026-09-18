import { describe, expect, it } from "vitest";
import {
  ACF_OCIO_ROLE,
  ADMIN_DASHBOARD_NAV_ITEMS,
  ADMIN_PRIMARY_NAV_ITEMS,
  DIGIT_TEAM_ROLE,
  getAdminNavigationTitle,
  getAdminRoleNames,
  getDefaultExpandedAdminNavIds,
  getVisibleAdminNavItems,
  isAdminNavItemActive,
  OFA_ADMIN_ROLE,
  OFA_SYSTEM_ADMIN_ROLE,
  type AdminNavItem,
} from "./admin-navigation";

describe("admin navigation helpers", () => {
  it("normalizes role names from Django role objects and local test strings", () => {
    expect(
      getAdminRoleNames([
        OFA_SYSTEM_ADMIN_ROLE,
        { id: 1, name: "Data Analyst", permissions: [] },
        { id: 2 },
      ])
    ).toEqual([OFA_SYSTEM_ADMIN_ROLE, "Data Analyst"]);
  });

  it("shows system-admin navigation to OFA System Admin users", () => {
    const items = getVisibleAdminNavItems([
      { id: 1, name: OFA_SYSTEM_ADMIN_ROLE, permissions: [] },
    ]);
    const dashboardItems = getVisibleAdminNavItems(
      [OFA_SYSTEM_ADMIN_ROLE],
      ADMIN_DASHBOARD_NAV_ITEMS
    );

    expect(items.map((item) => item.id)).toEqual([
      "home",
      "users",
      "log-entries",
      "data-files",
      "etl",
      "feature-flags",
      "parsers",
      "periodic-tasks",
      "reports",
      "search-indexes",
      "security",
      "stts",
      "appearance",
    ]);
    expect(
      items.find((item) => item.id === "users")?.children?.map((item) => item.id)
    ).toEqual(["user-accounts", "requests-authorization", "feedback"]);
    expect(dashboardItems.map((item) => item.id)).toEqual([
      "acf-ocio-dashboard",
      "digit-team-dashboard",
      "ofa-admin-dashboard",
    ]);
  });

  it("shows full navigation to Django admins without a TDP role", () => {
    const items = getVisibleAdminNavItems(
      [],
      ADMIN_PRIMARY_NAV_ITEMS,
      true
    );
    const dashboardItems = getVisibleAdminNavItems(
      [],
      ADMIN_DASHBOARD_NAV_ITEMS,
      true
    );

    expect(getAdminNavigationTitle([], true)).toBe("System Admin");
    expect(items.map((item) => item.id)).toEqual(
      ADMIN_PRIMARY_NAV_ITEMS.map((item) => item.id)
    );
    expect(dashboardItems.map((item) => item.id)).toEqual(
      ADMIN_DASHBOARD_NAV_ITEMS.map((item) => item.id)
    );
  });

  it("shows ACF OCIO navigation", () => {
    const items = getVisibleAdminNavItems([ACF_OCIO_ROLE]);

    expect(getAdminNavigationTitle([ACF_OCIO_ROLE])).toBe("ACF OCIO");
    expect(items.map((item) => item.id)).toEqual(["home", "security"]);
    expect(
      getVisibleAdminNavItems([ACF_OCIO_ROLE], ADMIN_DASHBOARD_NAV_ITEMS)
    ).toEqual([]);
  });

  it("shows DIGIT Team navigation", () => {
    const items = getVisibleAdminNavItems([DIGIT_TEAM_ROLE]);

    expect(getAdminNavigationTitle([DIGIT_TEAM_ROLE])).toBe("DIGIT Team");
    expect(items.map((item) => item.id)).toEqual([
      "home",
      "data-files",
      "etl",
      "parsers",
      "reports",
      "search-indexes",
      "stts",
    ]);
  });

  it("shows OFA Admin navigation", () => {
    const items = getVisibleAdminNavItems([OFA_ADMIN_ROLE]);

    expect(getAdminNavigationTitle([OFA_ADMIN_ROLE])).toBe("OFA Admin");
    expect(items.map((item) => item.id)).toEqual([
      "home",
      "users",
      "log-entries",
      "data-files",
      "reports",
      "security",
      "stts",
    ]);
  });

  it("hides admin navigation from unsupported roles", () => {
    expect(getVisibleAdminNavItems(["Data Analyst"])).toEqual([]);
    expect(getVisibleAdminNavItems()).toEqual([]);
  });

  it("marks linked navigation items active", () => {
    const homeItem = ADMIN_PRIMARY_NAV_ITEMS.find((item) => item.id === "home");
    const dataFilesItem = ADMIN_PRIMARY_NAV_ITEMS.find(
      (item) => item.id === "data-files"
    );

    expect(homeItem).toBeDefined();
    expect(dataFilesItem).toBeDefined();
    expect(isAdminNavItemActive("/dashboard", homeItem as AdminNavItem)).toBe(
      true
    );
    expect(
      isAdminNavItemActive("/data-files", dataFilesItem as AdminNavItem)
    ).toBe(false);
    expect(
      isAdminNavItemActive(
        "/users/123/edit",
        ADMIN_PRIMARY_NAV_ITEMS.find(
          (item) => item.id === "users"
        ) as AdminNavItem
      )
    ).toBe(true);
  });

  it("expands the Users group by default", () => {
    expect(
      getDefaultExpandedAdminNavIds("/dashboard", ADMIN_PRIMARY_NAV_ITEMS)
    ).toEqual(["users"]);
  });

  it("uses the system admin title for OFA System Admin users", () => {
    expect(getAdminNavigationTitle([OFA_SYSTEM_ADMIN_ROLE])).toBe(
      "System Admin"
    );
  });
});
