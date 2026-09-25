import { describe, expect, it } from "vitest";
import { getAdminRoleSummary } from "./admin-session-display";

describe("admin session display", () => {
  it("summarizes string roles", () => {
    expect(getAdminRoleSummary(["OFA System Admin", "Developer"])).toBe(
      "OFA System Admin, Developer"
    );
  });

  it("summarizes serialized Django group roles", () => {
    expect(
      getAdminRoleSummary([
        { id: 1, name: "OFA System Admin" },
        { id: 2, name: "Data Analyst" },
      ])
    ).toBe("OFA System Admin, Data Analyst");
  });

  it("falls back when no role labels are available", () => {
    expect(getAdminRoleSummary()).toBe("No roles returned");
    expect(getAdminRoleSummary([])).toBe("No roles returned");
  });
});

